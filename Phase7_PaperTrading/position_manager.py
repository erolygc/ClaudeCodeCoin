"""
Position Manager
Pozisyon açma, kapama ve yönetim modülü
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import config

logger = logging.getLogger(__name__)


class Position:
    """Tek bir pozisyonu temsil eder"""

    def __init__(self, symbol: str, entry_price: float, quantity: float,
                 confidence: float, stop_loss: float, take_profit: float,
                 position_id: Optional[int] = None):
        self.position_id = position_id
        self.symbol = symbol
        self.entry_price = entry_price
        self.quantity = quantity
        self.confidence = confidence
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = datetime.now()
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0.0
        self.status = "OPEN"  # OPEN, CLOSED
        self.close_reason = None  # TP, SL, MANUAL, TIMEOUT, TRAILING_STOP

        # Trailing stop
        self.highest_price = entry_price

    def update_highest_price(self, current_price: float):
        """Trailing stop için en yüksek fiyatı güncelle"""
        if current_price > self.highest_price:
            self.highest_price = current_price

    def check_exit_conditions(self, current_price: float) -> Optional[str]:
        """Çıkış koşullarını kontrol et"""
        # Stop Loss kontrolü
        if current_price <= self.stop_loss:
            return "SL"

        # Take Profit kontrolü
        if current_price >= self.take_profit:
            return "TP"

        # Trailing Stop kontrolü
        trailing_stop_price = self.highest_price * (1 - config.TRAILING_STOP_PERCENT / 100)
        if current_price <= trailing_stop_price:
            return "TRAILING_STOP"

        # Timeout kontrolü
        if datetime.now() - self.entry_time > timedelta(minutes=config.AUTO_CLOSE_AFTER_MINUTES):
            return "TIMEOUT"

        return None

    def close(self, exit_price: float, reason: str) -> float:
        """Pozisyonu kapat ve P&L hesapla"""
        self.exit_price = exit_price
        self.exit_time = datetime.now()
        self.status = "CLOSED"
        self.close_reason = reason

        # P&L hesaplama
        gross_pnl = (exit_price - self.entry_price) * self.quantity

        # İşlem ücretlerini düş
        entry_fee = self.entry_price * self.quantity * (config.TRADING_FEE_PERCENT / 100)
        exit_fee = exit_price * self.quantity * (config.TRADING_FEE_PERCENT / 100)
        total_fees = entry_fee + exit_fee

        self.pnl = gross_pnl - total_fees

        return self.pnl

    def to_dict(self) -> dict:
        """Pozisyonu dictionary'e çevir"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'confidence': self.confidence,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'pnl': self.pnl,
            'status': self.status,
            'close_reason': self.close_reason
        }


class PositionManager:
    """Tüm pozisyonları yöneten ana sınıf"""

    def __init__(self, db_path: str = config.TRADES_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.balance = config.INITIAL_BALANCE
        self.open_positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []

        self._init_database()
        self._load_state()

    def _init_database(self):
        """Veritabanını oluştur"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Pozisyonlar tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                position_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                confidence REAL NOT NULL,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                pnl REAL DEFAULT 0,
                status TEXT NOT NULL,
                close_reason TEXT
            )
        """)

        # Bakiye geçmişi tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                balance REAL NOT NULL,
                total_pnl REAL NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def _load_state(self):
        """Son durumu yükle"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Açık pozisyonları yükle
        cursor.execute("""
            SELECT position_id, symbol, entry_price, quantity, confidence,
                   stop_loss, take_profit, entry_time
            FROM positions
            WHERE status = 'OPEN'
        """)

        for row in cursor.fetchall():
            position = Position(
                symbol=row[1],
                entry_price=row[2],
                quantity=row[3],
                confidence=row[4],
                stop_loss=row[5],
                take_profit=row[6],
                position_id=row[0]
            )
            position.entry_time = datetime.fromisoformat(row[7])
            self.open_positions[row[1]] = position

        # Son bakiyeyi yükle
        cursor.execute("""
            SELECT balance FROM balance_history
            ORDER BY timestamp DESC LIMIT 1
        """)
        last_balance = cursor.fetchone()
        if last_balance:
            self.balance = last_balance[0]

        conn.close()
        logger.info(f"💰 Başlangıç bakiyesi: ${self.balance:.2f}")
        logger.info(f"📊 Açık pozisyon: {len(self.open_positions)} adet")

    def can_open_position(self, symbol: str, required_capital: float) -> Tuple[bool, str]:
        """Yeni pozisyon açılabilir mi kontrol et"""
        # Zaten bu sembolde pozisyon var mı?
        if symbol in self.open_positions:
            return False, f"Zaten {symbol} için açık pozisyon var"

        # Maksimum pozisyon sayısına ulaşıldı mı?
        if len(self.open_positions) >= config.MAX_OPEN_POSITIONS:
            return False, f"Maksimum {config.MAX_OPEN_POSITIONS} açık pozisyon sınırına ulaşıldı"

        # Yeterli bakiye var mı?
        if required_capital > self.balance:
            return False, f"Yetersiz bakiye. Gerekli: ${required_capital:.2f}, Mevcut: ${self.balance:.2f}"

        return True, "OK"

    def open_position(self, symbol: str, entry_price: float, confidence: float,
                     volume_spike: float) -> Optional[Position]:
        """Yeni pozisyon aç"""

        # Confidence seviyesini belirle
        if confidence >= 85:
            conf_level = 'CRITICAL'
        elif confidence >= 70:
            conf_level = 'HIGH'
        elif confidence >= 50:
            conf_level = 'MEDIUM'
        else:
            conf_level = 'LOW'

        # Pozisyon büyüklüğünü hesapla
        max_position_value = self.balance * (config.MAX_POSITION_SIZE_PERCENT / 100)
        position_multiplier = config.POSITION_SIZE_MULTIPLIER[conf_level]
        position_value = max_position_value * position_multiplier

        # Minimum pozisyon kontrolü
        if position_value < config.MIN_POSITION_SIZE:
            logger.warning(f"Pozisyon büyüklüğü minimum seviyenin altında: ${position_value:.2f}")
            return None

        # Pozisyon açılabilir mi kontrol et
        can_open, reason = self.can_open_position(symbol, position_value)
        if not can_open:
            logger.warning(f"❌ Pozisyon açılamadı: {reason}")
            return None

        # Quantity hesapla
        quantity = position_value / entry_price

        # Stop Loss ve Take Profit hesapla
        stop_loss = entry_price * (1 - config.STOP_LOSS_PERCENT / 100)
        take_profit_percent = config.TAKE_PROFIT_PERCENT[conf_level]
        take_profit = entry_price * (1 + take_profit_percent / 100)

        # Pozisyon oluştur
        position = Position(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            confidence=confidence,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        # Veritabanına kaydet
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO positions (symbol, entry_price, quantity, confidence,
                                 stop_loss, take_profit, entry_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')
        """, (symbol, entry_price, quantity, confidence, stop_loss, take_profit,
              position.entry_time.isoformat()))

        position.position_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Bakiyeden düş
        self.balance -= position_value

        # Açık pozisyonlara ekle
        self.open_positions[symbol] = position

        logger.info(f"✅ YENİ POZİSYON AÇILDI:")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Entry: ${entry_price:.4f}")
        logger.info(f"   Quantity: {quantity:.4f}")
        logger.info(f"   Value: ${position_value:.2f}")
        logger.info(f"   Confidence: {confidence:.1f}% ({conf_level})")
        logger.info(f"   Stop Loss: ${stop_loss:.4f} (-{config.STOP_LOSS_PERCENT}%)")
        logger.info(f"   Take Profit: ${take_profit:.4f} (+{take_profit_percent}%)")
        logger.info(f"   Kalan bakiye: ${self.balance:.2f}")

        return position

    def close_position(self, symbol: str, exit_price: float, reason: str) -> Optional[float]:
        """Pozisyonu kapat"""
        if symbol not in self.open_positions:
            logger.warning(f"❌ {symbol} için açık pozisyon bulunamadı")
            return None

        position = self.open_positions[symbol]

        # Pozisyonu kapat ve P&L hesapla
        pnl = position.close(exit_price, reason)

        # Veritabanını güncelle
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE positions
            SET exit_price = ?, exit_time = ?, pnl = ?, status = 'CLOSED', close_reason = ?
            WHERE position_id = ?
        """, (exit_price, position.exit_time.isoformat(), pnl, reason, position.position_id))

        conn.commit()
        conn.close()

        # Bakiyeye ekle
        position_value = exit_price * position.quantity
        self.balance += position_value

        # Kapalı pozisyonlara taşı
        self.closed_positions.append(position)
        del self.open_positions[symbol]

        # Bakiye geçmişini kaydet
        self._save_balance_snapshot()

        pnl_percent = (pnl / (position.entry_price * position.quantity)) * 100
        duration = (position.exit_time - position.entry_time).total_seconds() / 60

        logger.info(f"🔴 POZİSYON KAPANDI:")
        logger.info(f"   Symbol: {symbol}")
        logger.info(f"   Entry: ${position.entry_price:.4f}")
        logger.info(f"   Exit: ${exit_price:.4f}")
        logger.info(f"   P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)")
        logger.info(f"   Sebep: {reason}")
        logger.info(f"   Süre: {duration:.1f} dakika")
        logger.info(f"   Yeni bakiye: ${self.balance:.2f}")

        return pnl

    def update_positions(self, current_prices: Dict[str, float]):
        """Açık pozisyonları güncelle ve çıkış koşullarını kontrol et"""
        positions_to_close = []

        for symbol, position in self.open_positions.items():
            if symbol not in current_prices:
                continue

            current_price = current_prices[symbol]

            # En yüksek fiyatı güncelle (trailing stop için)
            position.update_highest_price(current_price)

            # Çıkış koşullarını kontrol et
            exit_reason = position.check_exit_conditions(current_price)
            if exit_reason:
                positions_to_close.append((symbol, current_price, exit_reason))

        # Pozisyonları kapat
        for symbol, price, reason in positions_to_close:
            self.close_position(symbol, price, reason)

    def _save_balance_snapshot(self):
        """Bakiye anlık görüntüsünü kaydet"""
        total_pnl = sum(p.pnl for p in self.closed_positions)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO balance_history (timestamp, balance, total_pnl)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), self.balance, total_pnl))

        conn.commit()
        conn.close()

    def get_portfolio_summary(self) -> dict:
        """Portföy özetini getir"""
        total_pnl = sum(p.pnl for p in self.closed_positions)
        winning_trades = [p for p in self.closed_positions if p.pnl > 0]
        losing_trades = [p for p in self.closed_positions if p.pnl <= 0]

        # Açık pozisyonların değerini hesapla (gerçek zamanlı fiyatlar gerekli)
        open_positions_value = 0

        return {
            'balance': self.balance,
            'initial_balance': config.INITIAL_BALANCE,
            'total_pnl': total_pnl,
            'total_pnl_percent': (total_pnl / config.INITIAL_BALANCE) * 100,
            'open_positions': len(self.open_positions),
            'total_trades': len(self.closed_positions),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.closed_positions) * 100) if self.closed_positions else 0,
            'avg_win': sum(p.pnl for p in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(p.pnl for p in losing_trades) / len(losing_trades) if losing_trades else 0
        }
