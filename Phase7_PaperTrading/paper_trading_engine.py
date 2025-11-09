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
        logger.info("======================================================================")
        logger.info("📋 Fiyat verisi olan coinler için işlem yapılacak")
        logger.info("⚠️  Yeni coinler collectors restart sonrası eklenecek")
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
            five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

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

    def check_price_data_available(self, symbol: str, exchange: str = "gate.io") -> bool:
        """Sembol için fiyat verisi mevcut mu kontrol et"""
        try:
            # Symbol formatını düzenle
            if exchange == "gate.io" and "_" not in symbol:
                symbol = symbol.replace("USDT", "_USDT")
            elif exchange == "binance" and "_" in symbol:
                symbol = symbol.replace("_", "")

            conn = sqlite3.connect(str(self.klines_db))
            cursor = conn.cursor()

            # Son 10 dakika içinde veri var mı kontrol et
            ten_mins_ago = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                SELECT COUNT(*) FROM klines
                WHERE symbol = ? AND exchange = ? AND datetime >= ?
            """, (symbol, exchange, ten_mins_ago))

            result = cursor.fetchone()
            conn.close()

            return result and result[0] > 0

        except Exception as e:
            logger.error(f"❌ Veri kontrolü hatası ({symbol}): {e}")
            return False

    def load_recent_alerts(self) -> List[dict]:
        """Son pump alert'lerini oku ve fiyat verisi olmayanları filtrele"""
        alerts = []

        try:
            # Bugünün alert dosyasını bul
            today = datetime.now().strftime("%Y%m%d")
            alert_file = self.alerts_file / f"pump_alerts_{today}.json"

            if not alert_file.exists():
                logger.info(f"ℹ️  Alert dosyası bulunamadı: {alert_file}")
                return alerts

            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Format hem direkt liste hem de dictionary içinde liste olabilir
                if isinstance(data, list):
                    alerts = data
                else:
                    alerts = data.get('alerts', [])

            logger.info(f"📄 Alert dosyasından {len(alerts)} toplam alert okundu")

            # TEST MODE: MIN_VOLUME_SPIKE=0 ise zaman filtresini devre dışı bırak
            # PRODUCTION MODE: Sadece son 10 dakikadaki alert'leri al
            if config.MIN_VOLUME_SPIKE == 0.0:
                # TEST MODE: Tüm alertleri kabul et (zaman fark etmez)
                recent_alerts = alerts
                logger.info(f"⏰ TEST MODE: Tüm {len(alerts)} alert işlenecek (zaman filtresi devre dışı)")
            else:
                # PRODUCTION MODE: Sadece son 10 dakika
                recent_alerts = []
                ten_mins_ago = datetime.now() - timedelta(minutes=10)

                for alert in alerts:
                    alert_time = datetime.fromisoformat(alert['timestamp'])
                    if alert_time >= ten_mins_ago:
                        recent_alerts.append(alert)

                logger.info(f"⏰ Son 10 dakikada {len(recent_alerts)} alert var")

            # Fiyat verisi olmayan coinleri filtrele
            valid_alerts = []
            skipped_coins = []
            valid_coins = []

            for alert in recent_alerts:
                symbol = alert['symbol']
                exchange = alert.get('exchange', 'gate.io')
                confidence = alert.get('confidence', 0)
                volume_change = alert.get('volume_change_pct', 0)

                if self.check_price_data_available(symbol, exchange):
                    valid_alerts.append(alert)
                    valid_coins.append(f"{symbol} ({confidence:.0f}%, {volume_change:.0f}%)")
                else:
                    skipped_coins.append(symbol)

            # İşlenecek coinleri göster
            if valid_coins:
                logger.info(f"✅ Fiyat verisi VAR ({len(valid_coins)} alert):")
                for coin_info in valid_coins[:5]:  # İlk 5'ini göster
                    logger.info(f"   └── {coin_info}")
                if len(valid_coins) > 5:
                    logger.info(f"   └── ... ve {len(valid_coins) - 5} tane daha")

            # Atlanan coinleri logla
            if skipped_coins:
                unique_skipped = list(set(skipped_coins))
                if len(unique_skipped) <= 5:
                    logger.info(f"⏭️  Fiyat verisi YOK (atlandı): {', '.join(unique_skipped)}")
                else:
                    logger.info(f"⏭️  {len(unique_skipped)} coin için fiyat verisi YOK (atlandı)")

            return valid_alerts

        except Exception as e:
            logger.error(f"❌ Alert'ler okunurken hata: {e}")
            return []

    def should_open_position(self, alert: dict) -> bool:
        """Bu alert için pozisyon açılmalı mı?"""
        symbol = alert['symbol']

        # Minimum confidence kontrolü
        if alert['confidence'] < config.MIN_CONFIDENCE_TO_TRADE:
            logger.info(f"   ⊘ {symbol}: Confidence çok düşük ({alert['confidence']:.1f}% < {config.MIN_CONFIDENCE_TO_TRADE}%)")
            return False

        # Minimum hacim spike kontrolü (volume_change_pct yüzde olarak geliyor)
        volume_change = alert.get('volume_change_pct', 0)
        # Sonsuz değerleri kontrol et
        if volume_change == float('inf') or volume_change == '∞':
            volume_change = 10000.0  # Çok yüksek hacim artışı olarak kabul et

        # TEST MODE: MIN_VOLUME_SPIKE = 0 ise tüm volume seviyelerini kabul et
        if config.MIN_VOLUME_SPIKE > 0 and volume_change < config.MIN_VOLUME_SPIKE:
            logger.info(f"   ⊘ {symbol}: Volume spike çok düşük ({volume_change:.0f}% < {config.MIN_VOLUME_SPIKE}%)")
            return False

        # Bu alert daha önce işlendi mi?
        alert_id = f"{alert['symbol']}_{alert['timestamp']}"
        if alert_id in self.processed_alerts:
            logger.info(f"   ⊘ {symbol}: Bu alert daha önce işlendi")
            return False

        # Zaten bu sembolde açık pozisyon var mı?
        if alert['symbol'] in self.position_manager.open_positions:
            logger.info(f"   ⊘ {symbol}: Bu coin için zaten açık pozisyon var")
            return False

        return True

    def process_alerts(self):
        """Yeni alert'leri işle ve pozisyon aç"""
        alerts = self.load_recent_alerts()

        if not alerts:
            logger.info("📭 İşlenecek yeni alert yok (fiyat verisi veya zaman filtresi)")
            return

        logger.info(f"📬 {len(alerts)} yeni alert bulundu (fiyat verisi mevcut olanlar)")

        for alert in alerts:
            if not self.should_open_position(alert):
                continue

            # Güncel fiyatı al
            current_price = self.get_current_price(alert['symbol'], alert.get('exchange', 'gate.io'))

            if current_price is None:
                continue

            # Pozisyon aç
            # volume_change_pct'yi volume_spike olarak kullan
            volume_change = alert.get('volume_change_pct', 0)
            if volume_change == float('inf') or volume_change == '∞':
                volume_change = 10000.0

            logger.info(f"🎯 {alert['symbol']} için pozisyon açılıyor...")
            logger.info(f"   └── Confidence: {alert['confidence']:.1f}%, Volume: {volume_change:.0f}%, Price: ${current_price:.4f}")

            position = self.position_manager.open_position(
                symbol=alert['symbol'],
                entry_price=current_price,
                confidence=alert['confidence'],
                volume_spike=volume_change
            )

            if position:
                logger.info(f"✅ Pozisyon açıldı: {alert['symbol']}")
                # Alert'i işlenmiş olarak işaretle
                alert_id = f"{alert['symbol']}_{alert['timestamp']}"
                self.processed_alerts.add(alert_id)

                # Çok fazla alert ID tutma (memory için)
                if len(self.processed_alerts) > 1000:
                    # En eskilerini sil
                    self.processed_alerts = set(list(self.processed_alerts)[-500:])
            else:
                logger.warning(f"⚠️  {alert['symbol']} için pozisyon açılamadı")

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
