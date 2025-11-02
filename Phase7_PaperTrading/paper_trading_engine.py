"""
Paper Trading Engine
Sanal trading motoru - Gerçek sinyaller ile sanal işlem yapar
"""

import sys
from pathlib import Path

# Proje kök dizinini ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Phase7_PaperTrading klasörünü de ekle
phase7_path = Path(__file__).parent
sys.path.insert(0, str(phase7_path))

import time
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import config
from position_manager import PositionManager

# Logs klasörünü oluştur
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'paper_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PaperTradingEngine:
    """Paper trading ana motoru"""

    def __init__(self):
        self.position_manager = PositionManager()
        self.klines_db = project_root / "data_output" / "binance_data.db"
        self.alerts_file = project_root / "pump_alerts"

        # Son işlenen alert'leri takip et (duplicate'leri önlemek için)
        self.processed_alerts = set()

        logger.info("======================================================================")
        logger.info("🚀 ClaudeCodeCoin - Paper Trading Engine")
        logger.info("======================================================================")
        logger.info(f"💰 Başlangıç bakiyesi: ${config.INITIAL_BALANCE:.2f}")
        logger.info(f"📊 Maksimum pozisyon: {config.MAX_OPEN_POSITIONS}")
        logger.info(f"🛡️  Stop Loss: {config.STOP_LOSS_PERCENT}%")
        logger.info(f"🎯 Take Profit: {config.TAKE_PROFIT_PERCENT}")
        logger.info(f"💵 Minimum confidence: {config.MIN_CONFIDENCE_TO_TRADE}%")
        logger.info("======================================================================\n")

    def get_current_price(self, symbol: str, exchange: str = "gate.io") -> Optional[float]:
        """Sembolin güncel fiyatını veritabanından al"""
        try:
            # Symbol formatını düzenle (Gate.io: BTC_USDT, Binance: BTCUSDT)
            if exchange == "gate.io" and "_" not in symbol:
                # BTCUSDT -> BTC_USDT
                symbol = symbol.replace("USDT", "_USDT")
            elif exchange == "binance" and "_" in symbol:
                # BTC_USDT -> BTCUSDT
                symbol = symbol.replace("_", "")

            conn = sqlite3.connect(str(self.klines_db))
            cursor = conn.cursor()

            # Son 5 dakika içindeki en son kapanış fiyatını al
            five_mins_ago = (datetime.now() - timedelta(minutes=5)).isoformat()

            cursor.execute("""
                SELECT close FROM klines
                WHERE symbol = ? AND exchange = ? AND datetime >= ?
                ORDER BY datetime DESC LIMIT 1
            """, (symbol, exchange, five_mins_ago))

            result = cursor.fetchone()
            conn.close()

            if result:
                return float(result[0])
            else:
                logger.warning(f"⚠️  {symbol} için güncel fiyat bulunamadı")
                return None

        except Exception as e:
            logger.error(f"❌ Fiyat alınırken hata: {e}")
            return None

    def load_recent_alerts(self) -> List[dict]:
        """Son pump alert'lerini oku"""
        alerts = []

        try:
            # Bugünün alert dosyasını bul
            today = datetime.now().strftime("%Y%m%d")
            alert_file = self.alerts_file / f"pump_alerts_{today}.json"

            if not alert_file.exists():
                return alerts

            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                alerts = data.get('alerts', [])

            # Sadece son 10 dakika içindeki alert'leri al
            recent_alerts = []
            ten_mins_ago = datetime.now() - timedelta(minutes=10)

            for alert in alerts:
                alert_time = datetime.fromisoformat(alert['timestamp'])
                if alert_time >= ten_mins_ago:
                    recent_alerts.append(alert)

            return recent_alerts

        except Exception as e:
            logger.error(f"❌ Alert'ler okunurken hata: {e}")
            return []

    def should_open_position(self, alert: dict) -> bool:
        """Bu alert için pozisyon açılmalı mı?"""

        # Minimum confidence kontrolü
        if alert['confidence'] < config.MIN_CONFIDENCE_TO_TRADE:
            return False

        # Minimum hacim spike kontrolü
        if alert.get('volume_spike', 0) < config.MIN_VOLUME_SPIKE:
            return False

        # Bu alert daha önce işlendi mi?
        alert_id = f"{alert['symbol']}_{alert['timestamp']}"
        if alert_id in self.processed_alerts:
            return False

        # Zaten bu sembolde açık pozisyon var mı?
        if alert['symbol'] in self.position_manager.open_positions:
            return False

        return True

    def process_alerts(self):
        """Yeni alert'leri işle ve pozisyon aç"""
        alerts = self.load_recent_alerts()

        for alert in alerts:
            if not self.should_open_position(alert):
                continue

            # Güncel fiyatı al
            current_price = self.get_current_price(alert['symbol'], alert.get('exchange', 'gate.io'))

            if current_price is None:
                continue

            # Pozisyon aç
            position = self.position_manager.open_position(
                symbol=alert['symbol'],
                entry_price=current_price,
                confidence=alert['confidence'],
                volume_spike=alert.get('volume_spike', 0)
            )

            if position:
                # Alert'i işlenmiş olarak işaretle
                alert_id = f"{alert['symbol']}_{alert['timestamp']}"
                self.processed_alerts.add(alert_id)

                # Çok fazla alert ID tutma (memory için)
                if len(self.processed_alerts) > 1000:
                    # En eskilerini sil
                    self.processed_alerts = set(list(self.processed_alerts)[-500:])

    def update_open_positions(self):
        """Açık pozisyonları güncelle ve exit koşullarını kontrol et"""
        if not self.position_manager.open_positions:
            return

        # Güncel fiyatları al
        current_prices = {}

        for symbol in self.position_manager.open_positions.keys():
            price = self.get_current_price(symbol, config.DEFAULT_EXCHANGE)
            if price:
                current_prices[symbol] = price

        # Pozisyonları güncelle
        self.position_manager.update_positions(current_prices)

    def print_status(self):
        """Durum raporunu yazdır"""
        summary = self.position_manager.get_portfolio_summary()

        logger.info("\n" + "="*70)
        logger.info("📊 PORTFÖY DURUMU")
        logger.info("="*70)
        logger.info(f"💰 Bakiye: ${summary['balance']:.2f}")
        logger.info(f"📈 Toplam P&L: ${summary['total_pnl']:.2f} ({summary['total_pnl_percent']:+.2f}%)")
        logger.info(f"📊 Açık Pozisyon: {summary['open_positions']}")
        logger.info(f"✅ Toplam İşlem: {summary['total_trades']}")

        if summary['total_trades'] > 0:
            logger.info(f"🎯 Win Rate: {summary['win_rate']:.1f}%")
            logger.info(f"   └── Kazanan: {summary['winning_trades']}, Kaybeden: {summary['losing_trades']}")
            logger.info(f"💵 Ortalama Kazanç: ${summary['avg_win']:.2f}")
            logger.info(f"💸 Ortalama Zarar: ${summary['avg_loss']:.2f}")

        logger.info("="*70 + "\n")

        # Açık pozisyonları listele
        if self.position_manager.open_positions:
            logger.info("📍 AÇIK POZİSYONLAR:")
            for symbol, pos in self.position_manager.open_positions.items():
                current_price = self.get_current_price(symbol, config.DEFAULT_EXCHANGE)
                if current_price:
                    unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
                    unrealized_pnl_pct = ((current_price / pos.entry_price) - 1) * 100

                    logger.info(f"  {symbol}:")
                    logger.info(f"    Entry: ${pos.entry_price:.4f}")
                    logger.info(f"    Current: ${current_price:.4f}")
                    logger.info(f"    P&L: ${unrealized_pnl:.2f} ({unrealized_pnl_pct:+.2f}%)")
                    logger.info(f"    SL: ${pos.stop_loss:.4f}, TP: ${pos.take_profit:.4f}")
            logger.info("")

    def run(self, interval_seconds: int = 30):
        """Ana döngüyü başlat"""
        logger.info("🔄 Paper trading başlatıldı...\n")

        iteration = 0

        try:
            while True:
                iteration += 1
                logger.info(f"🔍 İterasyon #{iteration} - {datetime.now().strftime('%H:%M:%S')}")

                # 1. Yeni alert'leri kontrol et ve pozisyon aç
                self.process_alerts()

                # 2. Açık pozisyonları güncelle
                self.update_open_positions()

                # 3. Her 10 iterasyonda durum raporu yazdır
                if iteration % 10 == 0:
                    self.print_status()

                # Bekle
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("\n⛔ Paper trading durduruldu")
            self.print_status()
            logger.info("👋 Görüşmek üzere!")


if __name__ == "__main__":
    # Logs klasörü oluştur
    Path("logs").mkdir(exist_ok=True)

    # Engine'i başlat
    engine = PaperTradingEngine()

    # Ana döngüyü başlat (her 30 saniyede bir kontrol)
    engine.run(interval_seconds=30)
