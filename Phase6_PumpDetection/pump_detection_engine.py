"""
ClaudeCodeCoin - Phase 6: Pump & Dump Detection Engine

Gerçek zamanlı pump ve dump tespiti için gelişmiş anomali algılama motoru.

Tespit Edilen Sinyaller:
- Anormal hacim artışları (3-10x spike)
- Hızlı fiyat hareketleri (%10-50+ artış)
- Order book dengesizlikleri
- Volatilite spike'ları
- Whale aktiviteleri
- Koordineli trading patternleri
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PumpSignalType(Enum):
    """Pump sinyal tipleri"""
    VOLUME_SPIKE = "volume_spike"
    PRICE_SURGE = "price_surge"
    VOLATILITY_SPIKE = "volatility_spike"
    ORDER_BOOK_IMBALANCE = "order_book_imbalance"
    WHALE_ACTIVITY = "whale_activity"
    COORDINATED_BUYING = "coordinated_buying"


class PumpLevel(Enum):
    """Pump seviyesi"""
    LOW = "low"           # 30-50% olasılık
    MEDIUM = "medium"     # 50-70% olasılık
    HIGH = "high"         # 70-85% olasılık
    CRITICAL = "critical" # 85%+ olasılık


@dataclass
class PumpSignal:
    """Pump sinyali veri sınıfı"""
    symbol: str
    exchange: str
    timestamp: datetime
    signal_type: PumpSignalType
    level: PumpLevel
    confidence: float  # 0-100
    price_change_pct: float
    volume_change_pct: float
    time_window_minutes: int
    current_price: float
    current_volume: float
    indicators: Dict
    message: str

    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'exchange': self.exchange,
            'timestamp': self.timestamp.isoformat(),
            'signal_type': self.signal_type.value,
            'level': self.level.value,
            'confidence': self.confidence,
            'price_change_pct': self.price_change_pct,
            'volume_change_pct': self.volume_change_pct,
            'time_window_minutes': self.time_window_minutes,
            'current_price': self.current_price,
            'current_volume': self.current_volume,
            'indicators': self.indicators,
            'message': self.message
        }


class PumpDetectionEngine:
    """
    Pump & Dump Tespit Motoru

    Özellikler:
    - Real-time anomaly detection
    - Multi-timeframe analizi
    - Çoklu sinyal kombinasyonu
    - Dinamik threshold ayarlama
    - False positive filtreleme
    """

    def __init__(self, db_path: str = "data_output/binance_data.db"):
        self.db_path = db_path

        # Tespit parametreleri
        self.params = {
            # Hacim Spike Parametreleri
            'volume_spike_threshold': 3.0,      # 3x normal hacim
            'extreme_volume_threshold': 5.0,    # 5x ekstrem hacim

            # Fiyat Değişim Parametreleri
            'price_surge_threshold': 10.0,      # %10 artış
            'extreme_price_threshold': 20.0,    # %20 ekstrem artış

            # Volatilite Parametreleri
            'volatility_spike_threshold': 2.5,  # 2.5x normal volatilite

            # Zaman Pencereleri (dakika)
            'short_window': 5,    # Kısa vadeli
            'medium_window': 15,  # Orta vadeli
            'long_window': 60,    # Uzun vadeli

            # Minimum veri gereksinimleri
            'min_bars_short': 10,
            'min_bars_medium': 30,
            'min_bars_long': 120,

            # Confidence eşikleri
            'low_confidence': 30.0,
            'medium_confidence': 50.0,
            'high_confidence': 70.0,
            'critical_confidence': 85.0
        }

    def analyze_symbol(self, symbol: str, exchange: str = "gate.io",
                      lookback_bars: int = 120) -> List[PumpSignal]:
        """
        Sembol için pump analizi yap

        Returns:
            Tespit edilen pump sinyalleri listesi
        """
        # Veriyi çek
        df = self._get_data(symbol, exchange, lookback_bars)

        if df is None or len(df) < self.params['min_bars_short']:
            logger.warning(f"Yetersiz veri: {symbol} - {len(df) if df is not None else 0} bars")
            return []

        # İndikatörleri hesapla
        df = self._calculate_indicators(df)

        # Sinyalleri tespit et
        signals = []

        # 1. Hacim Spike Analizi
        volume_signals = self._detect_volume_spike(df, symbol, exchange)
        signals.extend(volume_signals)

        # 2. Fiyat Surge Analizi
        price_signals = self._detect_price_surge(df, symbol, exchange)
        signals.extend(price_signals)

        # 3. Volatilite Spike Analizi
        volatility_signals = self._detect_volatility_spike(df, symbol, exchange)
        signals.extend(volatility_signals)

        # 4. Koordineli Alım Analizi
        coordinated_signals = self._detect_coordinated_buying(df, symbol, exchange)
        signals.extend(coordinated_signals)

        # 5. Sinyalleri birleştir ve skorla
        combined_signals = self._combine_signals(signals, df, symbol, exchange)

        # Confidence'a göre sırala
        combined_signals.sort(key=lambda x: x.confidence, reverse=True)

        return combined_signals

    def _get_data(self, symbol: str, exchange: str, limit: int) -> Optional[pd.DataFrame]:
        """Veritabanından veri çek"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT timestamp, datetime, open, high, low, close, volume
                FROM klines
                WHERE symbol = ? AND exchange = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(symbol, exchange, limit))
            conn.close()

            if df.empty:
                return None

            # Sıralama düzelt
            df = df.sort_values('timestamp')
            df.reset_index(drop=True, inplace=True)
            df['datetime'] = pd.to_datetime(df['datetime'])

            return df

        except Exception as e:
            logger.error(f"Veri çekme hatası: {e}")
            return None

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Teknik indikatörleri hesapla"""
        # Fiyat değişimleri
        df['price_change'] = df['close'].pct_change() * 100
        df['price_change_5'] = df['close'].pct_change(5) * 100
        df['price_change_15'] = df['close'].pct_change(15) * 100

        # Hacim değişimleri
        df['volume_change'] = df['volume'].pct_change() * 100
        df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_20']

        # Volatilite (ATR)
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift())
        df['low_close'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        df['atr_pct'] = (df['atr'] / df['close']) * 100

        # Volatilite ratio
        df['atr_ma'] = df['atr'].rolling(window=20).mean()
        df['volatility_ratio'] = df['atr'] / df['atr_ma']

        # Momentum
        df['rsi'] = self._calculate_rsi(df['close'], 14)

        # Hız (Rate of Change)
        df['roc_5'] = ((df['close'] - df['close'].shift(5)) / df['close'].shift(5)) * 100
        df['roc_15'] = ((df['close'] - df['close'].shift(15)) / df['close'].shift(15)) * 100

        return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI hesapla"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _detect_volume_spike(self, df: pd.DataFrame, symbol: str,
                            exchange: str) -> List[PumpSignal]:
        """Hacim spike tespiti"""
        signals = []

        if len(df) < 20:
            return signals

        latest = df.iloc[-1]

        # Volume ratio kontrolü
        volume_ratio = latest.get('volume_ratio', 0)

        if pd.isna(volume_ratio):
            return signals

        # Hacim spike varsa
        if volume_ratio >= self.params['volume_spike_threshold']:
            # Confidence hesapla
            confidence = 30 + (volume_ratio - 3) * 10

            # Fiyat değişimi de kontrole ekle
            price_change = latest.get('price_change_5', 0)
            if pd.isna(price_change):
                price_change = 0

            if price_change > 5:  # Hacim + Fiyat artışı = güçlü sinyal
                confidence += 15

            # Confidence'i 0-100 arasında tut
            confidence = max(0, min(100, confidence))

            # Seviye belirle
            if confidence >= self.params['critical_confidence']:
                level = PumpLevel.CRITICAL
            elif confidence >= self.params['high_confidence']:
                level = PumpLevel.HIGH
            elif confidence >= self.params['medium_confidence']:
                level = PumpLevel.MEDIUM
            else:
                level = PumpLevel.LOW

            # Calculate actual volume spike percentage
            # volume_ratio of 3.0 means 200% increase (3x = 300% of normal = +200%)
            # volume_ratio of 5.0 means 400% increase (5x = 500% of normal = +400%)
            volume_spike_pct = (volume_ratio - 1) * 100

            signal = PumpSignal(
                symbol=symbol,
                exchange=exchange,
                timestamp=latest['datetime'],
                signal_type=PumpSignalType.VOLUME_SPIKE,
                level=level,
                confidence=confidence,
                price_change_pct=price_change,
                volume_change_pct=volume_spike_pct,
                time_window_minutes=5,
                current_price=latest['close'],
                current_volume=latest['volume'],
                indicators={
                    'volume_ratio': float(volume_ratio),
                    'volume_ma_20': float(latest.get('volume_ma_20', 0)),
                    'rsi': float(latest.get('rsi', 50))
                },
                message=f"🔥 HACIM SPIKE: {volume_ratio:.1f}x normal hacim! "
                       f"Fiyat %{price_change:.1f} değişti."
            )

            signals.append(signal)

        return signals

    def _detect_price_surge(self, df: pd.DataFrame, symbol: str,
                           exchange: str) -> List[PumpSignal]:
        """Hızlı fiyat artışı tespiti"""
        signals = []

        if len(df) < 15:
            return signals

        latest = df.iloc[-1]

        # 5 ve 15 dakikalık fiyat değişimleri
        price_change_5 = latest.get('price_change_5', 0)
        price_change_15 = latest.get('price_change_15', 0)

        # Kısa vadeli surge
        if price_change_5 >= self.params['price_surge_threshold']:
            # Confidence hesapla
            confidence = 40 + (price_change_5 - 10) * 2

            # Hacim de artıyorsa confidence artır
            volume_ratio = latest.get('volume_ratio', 1)
            if pd.isna(volume_ratio):
                volume_ratio = 1
            if volume_ratio > 2:
                confidence += 15

            # RSI kontrolü
            rsi = latest.get('rsi', 50)
            if pd.isna(rsi):
                rsi = 50
            if rsi > 70:  # Aşırı alım
                confidence += 10

            # Confidence'i 0-100 arasında tut
            confidence = max(0, min(100, confidence))

            # Seviye belirle
            if confidence >= self.params['critical_confidence']:
                level = PumpLevel.CRITICAL
            elif confidence >= self.params['high_confidence']:
                level = PumpLevel.HIGH
            elif confidence >= self.params['medium_confidence']:
                level = PumpLevel.MEDIUM
            else:
                level = PumpLevel.LOW

            # Calculate actual volume spike percentage based on ratio
            volume_spike_pct = (volume_ratio - 1) * 100 if volume_ratio > 1 else 0

            signal = PumpSignal(
                symbol=symbol,
                exchange=exchange,
                timestamp=latest['datetime'],
                signal_type=PumpSignalType.PRICE_SURGE,
                level=level,
                confidence=confidence,
                price_change_pct=price_change_5,
                volume_change_pct=volume_spike_pct,
                time_window_minutes=5,
                current_price=latest['close'],
                current_volume=latest['volume'],
                indicators={
                    'price_change_5m': float(price_change_5),
                    'price_change_15m': float(price_change_15),
                    'volume_ratio': float(volume_ratio),
                    'rsi': float(rsi)
                },
                message=f"🚀 FİYAT SURGE: %{price_change_5:.1f} artış (5 dakika)! "
                       f"RSI: {rsi:.0f}"
            )

            signals.append(signal)

        return signals

    def _detect_volatility_spike(self, df: pd.DataFrame, symbol: str,
                                exchange: str) -> List[PumpSignal]:
        """Volatilite spike tespiti"""
        signals = []

        if len(df) < 20:
            return signals

        latest = df.iloc[-1]
        volatility_ratio = latest.get('volatility_ratio', 0)

        if pd.isna(volatility_ratio):
            return signals

        # Volatilite spike varsa
        if volatility_ratio >= self.params['volatility_spike_threshold']:
            confidence = 35 + (volatility_ratio - 2.5) * 12

            # Fiyat ve hacim değişimleri ekle
            price_change = abs(latest.get('price_change_5', 0))
            if pd.isna(price_change):
                price_change = 0

            volume_ratio = latest.get('volume_ratio', 1)
            if pd.isna(volume_ratio):
                volume_ratio = 1

            if price_change > 5 and volume_ratio > 2:
                confidence += 20

            # Confidence'i 0-100 arasında tut
            confidence = max(0, min(100, confidence))

            # Seviye belirle
            if confidence >= self.params['critical_confidence']:
                level = PumpLevel.CRITICAL
            elif confidence >= self.params['high_confidence']:
                level = PumpLevel.HIGH
            elif confidence >= self.params['medium_confidence']:
                level = PumpLevel.MEDIUM
            else:
                level = PumpLevel.LOW

            # Calculate actual volume spike percentage based on ratio
            volume_spike_pct = (volume_ratio - 1) * 100 if volume_ratio > 1 else 0

            signal = PumpSignal(
                symbol=symbol,
                exchange=exchange,
                timestamp=latest['datetime'],
                signal_type=PumpSignalType.VOLATILITY_SPIKE,
                level=level,
                confidence=confidence,
                price_change_pct=price_change,
                volume_change_pct=volume_spike_pct,
                time_window_minutes=5,
                current_price=latest['close'],
                current_volume=latest['volume'],
                indicators={
                    'volatility_ratio': float(volatility_ratio),
                    'atr_pct': float(latest.get('atr_pct', 0)),
                    'volume_ratio': float(volume_ratio)
                },
                message=f"⚡ VOLATİLİTE SPIKE: {volatility_ratio:.1f}x normal volatilite!"
            )

            signals.append(signal)

        return signals

    def _detect_coordinated_buying(self, df: pd.DataFrame, symbol: str,
                                  exchange: str) -> List[PumpSignal]:
        """Koordineli alım tespiti (sürekli yeşil barlar + hacim)"""
        signals = []

        if len(df) < 10:
            return signals

        # Son 5 bar'ı kontrol et
        last_5 = df.tail(5)

        # Kaç tanesi yeşil (close > open)?
        green_bars = (last_5['close'] > last_5['open']).sum()

        # Tümü yeşil mi?
        if green_bars >= 4:  # En az 4/5 yeşil
            latest = df.iloc[-1]

            # Toplam fiyat artışı
            total_price_change = ((latest['close'] - last_5.iloc[0]['open']) /
                                 last_5.iloc[0]['open']) * 100

            # Ortalama hacim ratio
            avg_volume_ratio = last_5['volume_ratio'].mean()

            if total_price_change > 5 and avg_volume_ratio > 1.5:
                confidence = 50 + total_price_change * 2
                # Confidence'i 0-100 arasında tut
                confidence = max(0, min(100, confidence))

                # Seviye belirle
                if confidence >= self.params['critical_confidence']:
                    level = PumpLevel.CRITICAL
                elif confidence >= self.params['high_confidence']:
                    level = PumpLevel.HIGH
                elif confidence >= self.params['medium_confidence']:
                    level = PumpLevel.MEDIUM
                else:
                    level = PumpLevel.LOW

                # Calculate actual volume spike percentage based on avg ratio
                volume_spike_pct = (avg_volume_ratio - 1) * 100 if avg_volume_ratio > 1 else 0

                rsi_val = latest.get('rsi', 50)
                if pd.isna(rsi_val):
                    rsi_val = 50

                signal = PumpSignal(
                    symbol=symbol,
                    exchange=exchange,
                    timestamp=latest['datetime'],
                    signal_type=PumpSignalType.COORDINATED_BUYING,
                    level=level,
                    confidence=confidence,
                    price_change_pct=total_price_change,
                    volume_change_pct=volume_spike_pct,
                    time_window_minutes=5,
                    current_price=latest['close'],
                    current_volume=latest['volume'],
                    indicators={
                        'green_bars': int(green_bars),
                        'avg_volume_ratio': float(avg_volume_ratio),
                        'rsi': float(rsi_val)
                    },
                    message=f"🎯 KOORDİNELİ ALIM: {green_bars}/5 yeşil bar! "
                           f"%{total_price_change:.1f} toplam artış."
                )

                signals.append(signal)

        return signals

    def _combine_signals(self, signals: List[PumpSignal], df: pd.DataFrame,
                        symbol: str, exchange: str) -> List[PumpSignal]:
        """
        Çoklu sinyalleri birleştir ve kombine confidence hesapla

        Aynı anda birden fazla sinyal varsa confidence artır
        """
        if len(signals) <= 1:
            return signals

        # Aynı timestamp'teki sinyalleri grupla
        latest_timestamp = df.iloc[-1]['datetime']
        recent_signals = [s for s in signals
                         if (latest_timestamp - s.timestamp).total_seconds() < 300]

        if len(recent_signals) > 1:
            # Kombine signal oluştur
            max_confidence = max(s.confidence for s in recent_signals)
            combined_confidence = max_confidence + (len(recent_signals) - 1) * 10
            # Confidence'i 0-100 arasında tut
            combined_confidence = max(0, min(100, combined_confidence))

            # En yüksek seviyeyi al
            levels_order = [PumpLevel.LOW, PumpLevel.MEDIUM, PumpLevel.HIGH, PumpLevel.CRITICAL]
            max_level = max((s.level for s in recent_signals),
                          key=lambda x: levels_order.index(x))

            latest = df.iloc[-1]

            signal_types = [s.signal_type.value for s in recent_signals]

            # NaN değerleri handle et
            price_change_val = latest.get('price_change_5', 0)
            if pd.isna(price_change_val):
                price_change_val = 0

            # Calculate actual volume spike percentage based on ratio
            volume_ratio = latest.get('volume_ratio', 1)
            if pd.isna(volume_ratio):
                volume_ratio = 1
            volume_spike_pct = (volume_ratio - 1) * 100 if volume_ratio > 1 else 0

            combined = PumpSignal(
                symbol=symbol,
                exchange=exchange,
                timestamp=latest_timestamp,
                signal_type=PumpSignalType.COORDINATED_BUYING,  # Genel tip
                level=max_level,
                confidence=combined_confidence,
                price_change_pct=price_change_val,
                volume_change_pct=volume_spike_pct,
                time_window_minutes=5,
                current_price=latest['close'],
                current_volume=latest['volume'],
                indicators={
                    'combined_signals': len(recent_signals),
                    'signal_types': signal_types,
                    'max_individual_confidence': max_confidence
                },
                message=f"🔥🔥 ÇOKLU SİNYAL: {len(recent_signals)} farklı pump göstergesi! "
                       f"({', '.join(signal_types)})"
            )

            return [combined] + signals

        return signals

    def scan_all_symbols(self, exchange: str = "gate.io") -> Dict[str, List[PumpSignal]]:
        """Tüm sembolleri tara"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT DISTINCT symbol FROM klines WHERE exchange = ?"
            df = pd.read_sql_query(query, conn, params=(exchange,))
            conn.close()

            results = {}

            for symbol in df['symbol']:
                logger.info(f"Taranıyor: {symbol}")
                signals = self.analyze_symbol(symbol, exchange)

                if signals:
                    results[symbol] = signals
                    logger.info(f"✅ {symbol}: {len(signals)} sinyal bulundu")

            return results

        except Exception as e:
            logger.error(f"Tarama hatası: {e}")
            return {}


# Test fonksiyonu
def test_pump_detection():
    """Pump detection test"""
    print("="*70)
    print("🔍 PUMP & DUMP DETECTION TEST")
    print("="*70)
    print()

    engine = PumpDetectionEngine()

    # BTC_USDT'yi analiz et
    print("Analyzing BTC_USDT on gate.io...")
    signals = engine.analyze_symbol("BTC_USDT", "gate.io")

    if signals:
        print(f"\n✅ {len(signals)} sinyal bulundu:\n")

        for i, signal in enumerate(signals, 1):
            print(f"{i}. {signal.message}")
            print(f"   Seviye: {signal.level.value.upper()}")
            print(f"   Confidence: {signal.confidence:.1f}%")
            print(f"   Fiyat Değişimi: %{signal.price_change_pct:.2f}")
            print(f"   Hacim Değişimi: %{signal.volume_change_pct:.2f}")
            print(f"   Zaman: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    else:
        print("❌ Henüz pump sinyali tespit edilmedi.")
        print("   (Normal piyasa koşulları)")

    print("="*70)


if __name__ == "__main__":
    test_pump_detection()
