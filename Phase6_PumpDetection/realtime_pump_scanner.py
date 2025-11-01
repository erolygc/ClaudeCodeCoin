"""
ClaudeCodeCoin - Real-Time Pump Scanner

Sürekli çalışan pump tespit sistemi.
Tüm sembolleri gerçek zamanlı tarar ve pump sinyalleri bulur.
"""

import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging

from pump_detection_engine import PumpDetectionEngine, PumpSignal, PumpLevel

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealtimePumpScanner:
    """
    Gerçek zamanlı pump tarayıcı

    Özellikler:
    - Tüm sembolleri periyodik olarak tarar
    - Pump sinyallerini tespit eder
    - Alert geçmişi tutar
    - JSON dosyasına kaydeder
    """

    def __init__(self, db_path: str = "data_output/binance_data.db",
                 output_dir: str = "pump_alerts"):
        self.engine = PumpDetectionEngine(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Alert geçmişi
        self.alert_history: List[Dict] = []
        self.last_alerts: Dict[str, datetime] = {}  # Symbol -> last alert time

        # Ayarlar
        self.scan_interval = 60  # Her 60 saniyede bir tara
        self.alert_cooldown = 300  # Aynı coin için 5 dakika cooldown

    def start_scanning(self, exchange: str = "gate.io"):
        """Taramayı başlat"""
        logger.info(f"🚀 Real-time Pump Scanner başlatıldı")
        logger.info(f"📊 Exchange: {exchange}")
        logger.info(f"⏱️  Tarama aralığı: {self.scan_interval} saniye")
        logger.info(f"🔔 Alert cooldown: {self.alert_cooldown} saniye")
        logger.info("="*70)

        scan_count = 0

        try:
            while True:
                scan_count += 1
                start_time = time.time()

                logger.info(f"\n🔍 Tarama #{scan_count} başladı...")

                # Tüm sembolleri tara
                results = self.engine.scan_all_symbols(exchange)

                # Sinyalleri işle
                new_alerts = 0
                for symbol, signals in results.items():
                    for signal in signals:
                        if self._should_alert(symbol, signal):
                            self._create_alert(signal)
                            new_alerts += 1

                elapsed = time.time() - start_time

                logger.info(f"✅ Tarama #{scan_count} tamamlandı ({elapsed:.1f}s)")
                logger.info(f"   Taranan sembol: {len(results)}")
                logger.info(f"   Yeni alert: {new_alerts}")

                # Sonuçları kaydet
                self._save_results()

                # Bekleme
                time.sleep(self.scan_interval)

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Scanner durduruldu")
            self._save_results()
            logger.info(f"📁 Toplam {len(self.alert_history)} alert kaydedildi")

    def _should_alert(self, symbol: str, signal: PumpSignal) -> bool:
        """Bu sinyal için alert oluşturulmalı mı?"""

        # Minimum confidence kontrolü
        if signal.confidence < 50:
            return False

        # Cooldown kontrolü
        if symbol in self.last_alerts:
            last_alert_time = self.last_alerts[symbol]
            elapsed = (datetime.now() - last_alert_time).total_seconds()

            if elapsed < self.alert_cooldown:
                return False

        return True

    def _create_alert(self, signal: PumpSignal):
        """Alert oluştur"""
        # Log
        emoji = self._get_level_emoji(signal.level)
        logger.warning(f"\n{emoji} PUMP ALERT: {signal.symbol}")
        logger.warning(f"   {signal.message}")
        logger.warning(f"   Confidence: {signal.confidence:.1f}%")
        logger.warning(f"   Price: ${signal.current_price:.4f}")

        # Geçmişe ekle
        self.alert_history.append(signal.to_dict())

        # Son alert zamanını güncelle
        self.last_alerts[signal.symbol] = datetime.now()

    def _get_level_emoji(self, level: PumpLevel) -> str:
        """Seviyeye göre emoji"""
        if level == PumpLevel.CRITICAL:
            return "🔴🔴🔴"
        elif level == PumpLevel.HIGH:
            return "🔴🔴"
        elif level == PumpLevel.MEDIUM:
            return "🟡"
        else:
            return "🟢"

    def _save_results(self):
        """Sonuçları kaydet"""
        if not self.alert_history:
            return

        # JSON dosyasına kaydet
        timestamp = datetime.now().strftime("%Y%m%d")
        output_file = self.output_dir / f"pump_alerts_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.alert_history, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Alerts kaydedildi: {output_file}")

    def get_recent_alerts(self, minutes: int = 60) -> List[Dict]:
        """Son N dakikanın alertleri"""
        now = datetime.now()
        cutoff = now.timestamp() - (minutes * 60)

        recent = []
        for alert in self.alert_history:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time.timestamp() > cutoff:
                recent.append(alert)

        return recent

    def get_alert_summary(self) -> Dict:
        """Alert özeti"""
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'by_level': {},
                'by_symbol': {},
                'recent_1h': 0,
                'recent_24h': 0
            }

        # Seviyeye göre
        by_level = {}
        for alert in self.alert_history:
            level = alert['level']
            by_level[level] = by_level.get(level, 0) + 1

        # Sembole göre
        by_symbol = {}
        for alert in self.alert_history:
            symbol = alert['symbol']
            by_symbol[symbol] = by_symbol.get(symbol, 0) + 1

        # Zaman bazlı
        now = datetime.now()
        recent_1h = len([a for a in self.alert_history
                        if (now - datetime.fromisoformat(a['timestamp'])).total_seconds() < 3600])
        recent_24h = len([a for a in self.alert_history
                         if (now - datetime.fromisoformat(a['timestamp'])).total_seconds() < 86400])

        return {
            'total_alerts': len(self.alert_history),
            'by_level': by_level,
            'by_symbol': by_symbol,
            'recent_1h': recent_1h,
            'recent_24h': recent_24h
        }


def main():
    """Scanner'ı başlat"""
    print("="*70)
    print("🚀 ClaudeCodeCoin - Real-Time Pump Scanner")
    print("="*70)
    print()
    print("Tüm coinleri sürekli tarayacak ve pump sinyalleri tespit edecek.")
    print()
    print("Durdurmak için: Ctrl+C")
    print("="*70)
    print()

    scanner = RealtimePumpScanner()
    scanner.start_scanning(exchange="gate.io")


if __name__ == "__main__":
    main()
