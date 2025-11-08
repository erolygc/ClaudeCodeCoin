"""
Advanced Multi-Timeframe Signal Engine
Uses 100+ indicators across multiple timeframes for high-accuracy signals
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from timeframe_aggregator import TimeframeAggregator
from indicator_calculator import IndicatorCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AdvancedSignal:
    """Advanced signal with multi-timeframe analysis"""
    symbol: str
    timestamp: str
    direction: str  # 'LONG' or 'SHORT'

    # Composite scores (0-100)
    overall_confidence: float
    trend_score: float
    momentum_score: float
    volume_score: float
    volatility_score: float
    pattern_score: float
    multi_tf_score: float

    # Entry/Exit levels
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float

    # Position sizing
    recommended_position_size: float
    risk_score: float  # 0-100, lower is better

    # Supporting data
    timeframes_analyzed: List[str]
    indicators_count: int
    key_indicators: Dict[str, float]

    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp,
            'direction': self.direction,
            'overall_confidence': self.overall_confidence,
            'scores': {
                'trend': self.trend_score,
                'momentum': self.momentum_score,
                'volume': self.volume_score,
                'volatility': self.volatility_score,
                'pattern': self.pattern_score,
                'multi_tf': self.multi_tf_score
            },
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_reward_ratio': self.risk_reward_ratio,
            'recommended_position_size': self.recommended_position_size,
            'risk_score': self.risk_score,
            'timeframes_analyzed': self.timeframes_analyzed,
            'indicators_count': self.indicators_count,
            'key_indicators': self.key_indicators
        }


class AdvancedSignalEngine:
    """
    Advanced Signal Generation Engine

    Features:
    - Multi-timeframe analysis (1m, 5m, 15m, 1h, 4h)
    - 100+ technical indicators
    - Composite scoring system
    - Risk-adjusted position sizing
    - High-accuracy signal filtering
    """

    # Timeframes to analyze (in order of importance)
    TIMEFRAMES = ['1h', '15m', '5m', '1m']  # Higher timeframes more important

    # Weights for composite score
    SCORE_WEIGHTS = {
        'trend': 0.25,
        'momentum': 0.25,
        'volume': 0.20,
        'volatility': 0.10,
        'pattern': 0.10,
        'multi_tf': 0.10
    }

    def __init__(self,
                 db_path: str = None,
                 multi_tf_dir: str = None,
                 min_confidence: float = 70.0):
        """
        Initialize Advanced Signal Engine

        Args:
            db_path: Path to source database (default: auto-detect)
            multi_tf_dir: Multi-timeframe data directory (default: auto-detect)
            min_confidence: Minimum confidence threshold (0-100)
        """
        self.aggregator = TimeframeAggregator(db_path, multi_tf_dir)
        self.indicator_calc = IndicatorCalculator()
        self.min_confidence = min_confidence

        logger.info("=" * 80)
        logger.info("ADVANCED SIGNAL ENGINE")
        logger.info("=" * 80)
        logger.info(f"Timeframes: {self.TIMEFRAMES}")
        logger.info(f"Min Confidence: {min_confidence}%")
        logger.info(f"Score Weights: {self.SCORE_WEIGHTS}")
        logger.info("=" * 80)

    def analyze_symbol(self, symbol: str, exchange: str = "gate.io") -> Optional[AdvancedSignal]:
        """
        Analyze symbol across all timeframes with all indicators

        Args:
            symbol: Trading pair
            exchange: Exchange name

        Returns:
            AdvancedSignal if signal meets criteria, else None
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing {symbol}")
        logger.info(f"{'='*60}")

        # Step 1: Collect multi-timeframe data with indicators
        tf_data = {}
        for tf in self.TIMEFRAMES:
            df = self.aggregator.load_timeframe_data(symbol, tf)

            if df is None or df.empty or len(df) < 50:
                logger.warning(f"  ⚠️ {tf}: Insufficient data")
                continue

            # Calculate all indicators
            df = self.indicator_calc.calculate_all_indicators(df)
            tf_data[tf] = df

            logger.info(f"  ✅ {tf}: {len(df)} bars, {len(df.columns)} features")

        if not tf_data:
            logger.warning(f"  ❌ No timeframe data available")
            return None

        # Step 2: Calculate scores for each component
        scores = self._calculate_composite_scores(tf_data)

        logger.info(f"\n  📊 Component Scores:")
        for component, score in scores.items():
            logger.info(f"     {component}: {score:.1f}/100")

        # Step 3: Calculate overall confidence
        overall_confidence = sum(
            scores[component] * self.SCORE_WEIGHTS[component]
            for component in scores.keys()
        )

        logger.info(f"\n  🎯 Overall Confidence: {overall_confidence:.1f}%")

        # Filter by minimum confidence
        if overall_confidence < self.min_confidence:
            logger.info(f"  ❌ Below minimum confidence ({self.min_confidence}%)")
            return None

        # Step 4: Determine direction
        direction = self._determine_direction(tf_data, scores)
        logger.info(f"  📈 Direction: {direction}")

        # Step 5: Calculate entry/exit levels
        entry_price, stop_loss, take_profit = self._calculate_levels(tf_data, direction)

        risk_reward = abs(take_profit - entry_price) / abs(entry_price - stop_loss) if entry_price != stop_loss else 0

        logger.info(f"\n  💰 Price Levels:")
        logger.info(f"     Entry: ${entry_price:.6f}")
        logger.info(f"     Stop Loss: ${stop_loss:.6f} ({((stop_loss - entry_price) / entry_price * 100):.2f}%)")
        logger.info(f"     Take Profit: ${take_profit:.6f} (+{((take_profit - entry_price) / entry_price * 100):.2f}%)")
        logger.info(f"     R:R Ratio: 1:{risk_reward:.2f}")

        # Step 6: Calculate position sizing
        risk_score = self._calculate_risk_score(tf_data, scores)
        position_size = self._calculate_position_size(overall_confidence, risk_score)

        logger.info(f"\n  ⚖️ Risk Management:")
        logger.info(f"     Risk Score: {risk_score:.1f}/100")
        logger.info(f"     Position Size: ${position_size:.2f}")

        # Step 7: Extract key indicators
        key_indicators = self._extract_key_indicators(tf_data)

        # Step 8: Create signal
        signal = AdvancedSignal(
            symbol=symbol,
            timestamp=tf_data['1m']['datetime'].iloc[-1].isoformat() if '1m' in tf_data else "",
            direction=direction,
            overall_confidence=overall_confidence,
            trend_score=scores['trend'],
            momentum_score=scores['momentum'],
            volume_score=scores['volume'],
            volatility_score=scores['volatility'],
            pattern_score=scores['pattern'],
            multi_tf_score=scores['multi_tf'],
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward,
            recommended_position_size=position_size,
            risk_score=risk_score,
            timeframes_analyzed=list(tf_data.keys()),
            indicators_count=len(tf_data[list(tf_data.keys())[0]].columns),
            key_indicators=key_indicators
        )

        logger.info(f"\n  ✅ SIGNAL GENERATED")
        logger.info(f"  {'='*60}\n")

        return signal

    def _calculate_composite_scores(self, tf_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate scores for each component"""
        scores = {}

        # TREND SCORE
        scores['trend'] = self._calculate_trend_score(tf_data)

        # MOMENTUM SCORE
        scores['momentum'] = self._calculate_momentum_score(tf_data)

        # VOLUME SCORE
        scores['volume'] = self._calculate_volume_score(tf_data)

        # VOLATILITY SCORE
        scores['volatility'] = self._calculate_volatility_score(tf_data)

        # PATTERN SCORE
        scores['pattern'] = self._calculate_pattern_score(tf_data)

        # MULTI-TIMEFRAME CONFLUENCE SCORE
        scores['multi_tf'] = self._calculate_multi_tf_score(tf_data)

        return scores

    def _calculate_trend_score(self, tf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate trend alignment score (0-100)"""
        scores = []

        for tf, df in tf_data.items():
            latest = df.iloc[-1]
            score = 50  # Neutral baseline

            # EMA alignment (20, 50, 100)
            if 'ema_20' in df.columns and 'ema_50' in df.columns:
                if latest['close'] > latest['ema_20'] > latest['ema_50']:
                    score += 20  # Strong uptrend
                elif latest['close'] < latest['ema_20'] < latest['ema_50']:
                    score -= 20  # Strong downtrend

            # MACD
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                if latest['macd'] > latest['macd_signal']:
                    score += 10
                else:
                    score -= 10

            # ADX (trend strength)
            if 'adx' in df.columns:
                if latest['adx'] > 25:
                    score += 10  # Strong trend
                elif latest['adx'] < 20:
                    score -= 5  # Weak trend

            # Supertrend
            if 'supertrend_direction' in df.columns:
                if latest['supertrend_direction'] == 1:
                    score += 10
                else:
                    score -= 10

            scores.append(max(0, min(100, score)))

        return np.mean(scores) if scores else 50

    def _calculate_momentum_score(self, tf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate momentum score (0-100)"""
        scores = []

        for tf, df in tf_data.items():
            latest = df.iloc[-1]
            score = 50

            # RSI
            if 'rsi_14' in df.columns:
                rsi = latest['rsi_14']
                if 40 <= rsi <= 65:
                    score += 20  # Optimal zone
                elif rsi > 70:
                    score -= 10  # Overbought
                elif rsi < 30:
                    score -= 10  # Oversold

            # Stochastic
            if 'stoch_k' in df.columns:
                stoch = latest['stoch_k']
                if 20 <= stoch <= 80:
                    score += 10
                elif stoch > 80 or stoch < 20:
                    score -= 5

            # ROC
            if 'roc_10' in df.columns:
                roc = latest['roc_10']
                if roc > 5:
                    score += 15
                elif roc < -5:
                    score -= 15

            # CCI
            if 'cci' in df.columns:
                cci = latest['cci']
                if -100 <= cci <= 100:
                    score += 5
                elif cci > 200 or cci < -200:
                    score -= 10

            scores.append(max(0, min(100, score)))

        return np.mean(scores) if scores else 50

    def _calculate_volume_score(self, tf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate volume confirmation score (0-100)"""
        scores = []

        for tf, df in tf_data.items():
            latest = df.iloc[-1]
            score = 50

            # Volume spike
            if len(df) >= 20:
                volume_ma = df['volume'].iloc[-20:].mean()
                volume_ratio = latest['volume'] / volume_ma if volume_ma > 0 else 1

                if volume_ratio > 2.0:
                    score += 25  # Strong volume
                elif volume_ratio > 1.5:
                    score += 15
                elif volume_ratio < 0.5:
                    score -= 15

            # OBV trend
            if 'obv' in df.columns and len(df) >= 10:
                obv_trend = df['obv'].iloc[-1] > df['obv'].iloc[-10]
                price_trend = df['close'].iloc[-1] > df['close'].iloc[-10]
                if obv_trend == price_trend:
                    score += 15  # Confirmation
                else:
                    score -= 10  # Divergence

            # MFI
            if 'mfi' in df.columns:
                mfi = latest['mfi']
                if 40 <= mfi <= 60:
                    score += 10

            scores.append(max(0, min(100, score)))

        return np.mean(scores) if scores else 50

    def _calculate_volatility_score(self, tf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate volatility risk score (0-100, higher = safer)"""
        scores = []

        for tf, df in tf_data.items():
            latest = df.iloc[-1]
            score = 50

            # ATR relative to price
            if 'atr_percent' in df.columns:
                atr_pct = latest['atr_percent']
                if 1 <= atr_pct <= 3:
                    score += 20  # Optimal volatility
                elif atr_pct > 5:
                    score -= 20  # Too volatile
                elif atr_pct < 0.5:
                    score -= 10  # Too quiet

            # Bollinger Band width
            if 'bb_width' in df.columns:
                bb_width = latest['bb_width']
                if 2 <= bb_width <= 5:
                    score += 15

            # Historical volatility
            if 'hist_volatility' in df.columns:
                hv = latest['hist_volatility']
                if hv < 50:
                    score += 15

            scores.append(max(0, min(100, score)))

        return np.mean(scores) if scores else 50

    def _calculate_pattern_score(self, tf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate pattern recognition score (0-100)"""
        scores = []

        for tf, df in tf_data.items():
            if len(df) < 10:
                continue

            score = 50
            latest = df.iloc[-1]

            # Consecutive green/red candles
            last_5 = df.tail(5)
            green_candles = (last_5['close'] > last_5['open']).sum()

            if green_candles >= 4:
                score += 20  # Strong bullish pattern
            elif green_candles <= 1:
                score -= 20  # Strong bearish pattern

            # Price above/below key levels
            if 'sma_50' in df.columns:
                if latest['close'] > latest['sma_50']:
                    score += 10
                else:
                    score -= 10

            # Breakout detection (price near high)
            if len(df) >= 20:
                high_20 = df['high'].iloc[-20:].max()
                if latest['close'] >= high_20 * 0.98:
                    score += 15  # Near breakout

            scores.append(max(0, min(100, score)))

        return np.mean(scores) if scores else 50

    def _calculate_multi_tf_score(self, tf_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate multi-timeframe confluence score (0-100)"""
        if len(tf_data) < 2:
            return 50

        # Check if trends align across timeframes
        trends = []
        for tf, df in tf_data.items():
            if len(df) < 20:
                continue

            # Determine trend direction
            latest = df.iloc[-1]
            prev = df.iloc[-10] if len(df) >= 10 else df.iloc[0]

            if 'ema_20' in df.columns:
                trend = 1 if latest['close'] > latest['ema_20'] else -1
            else:
                trend = 1 if latest['close'] > prev['close'] else -1

            trends.append(trend)

        if not trends:
            return 50

        # All aligned = 100, none aligned = 0
        aligned = sum(1 for t in trends if t == trends[0])
        score = (aligned / len(trends)) * 100

        return score

    def _determine_direction(self, tf_data: Dict[str, pd.DataFrame], scores: Dict[str, float]) -> str:
        """Determine LONG or SHORT direction"""
        # Use 1m timeframe as primary
        if '1m' not in tf_data:
            return 'LONG'  # Default

        df = tf_data['1m']
        latest = df.iloc[-1]

        bullish_signals = 0
        bearish_signals = 0

        # Check key indicators
        if 'ema_20' in df.columns:
            if latest['close'] > latest['ema_20']:
                bullish_signals += 1
            else:
                bearish_signals += 1

        if 'macd' in df.columns:
            if latest['macd'] > latest.get('macd_signal', 0):
                bullish_signals += 1
            else:
                bearish_signals += 1

        if 'rsi_14' in df.columns:
            if latest['rsi_14'] > 50:
                bullish_signals += 1
            else:
                bearish_signals += 1

        # Check overall scores
        if scores['trend'] > 50:
            bullish_signals += 1
        else:
            bearish_signals += 1

        return 'LONG' if bullish_signals > bearish_signals else 'SHORT'

    def _calculate_levels(self, tf_data: Dict[str, pd.DataFrame], direction: str) -> Tuple[float, float, float]:
        """Calculate entry, stop loss, and take profit levels"""
        # Use 1m for entry, fallback to other timeframes
        if '1m' in tf_data:
            df = tf_data['1m']
        elif '5m' in tf_data:
            df = tf_data['5m']
        else:
            df = list(tf_data.values())[0]

        latest = df.iloc[-1]

        entry_price = float(latest['close'])

        # ATR-based stop loss
        atr = float(latest.get('atr', entry_price * 0.02))  # Default 2%

        if direction == 'LONG':
            stop_loss = entry_price - (atr * 1.5)
            take_profit = entry_price + (atr * 4.5)  # 1:3 R:R
        else:
            stop_loss = entry_price + (atr * 1.5)
            take_profit = entry_price - (atr * 4.5)

        return entry_price, stop_loss, take_profit

    def _calculate_risk_score(self, tf_data: Dict[str, pd.DataFrame], scores: Dict[str, float]) -> float:
        """Calculate risk score (0-100, lower is better)"""
        # Inverse of volatility score
        risk = 100 - scores['volatility']

        # Adjust based on overall confidence
        overall = sum(scores[k] * self.SCORE_WEIGHTS[k] for k in scores.keys())
        risk = risk * (100 / max(overall, 1))

        return max(0, min(100, risk))

    def _calculate_position_size(self, confidence: float, risk_score: float) -> float:
        """Calculate recommended position size based on confidence and risk"""
        base_size = 100.0  # $100 base

        # Increase size with confidence
        confidence_multiplier = confidence / 100

        # Decrease size with risk
        risk_multiplier = (100 - risk_score) / 100

        position_size = base_size * confidence_multiplier * risk_multiplier

        # Clamp to reasonable range
        return max(50, min(200, position_size))

    def _extract_key_indicators(self, tf_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Extract key indicator values for reference"""
        if '1m' not in tf_data:
            return {}

        df = tf_data['1m']
        latest = df.iloc[-1]

        key_indicators = {}

        for col in ['rsi_14', 'macd', 'adx', 'cci', 'mfi', 'atr', 'bb_width', 'obv']:
            if col in df.columns:
                key_indicators[col] = float(latest[col]) if not pd.isna(latest[col]) else 0.0

        return key_indicators


def test_advanced_engine():
    """Test advanced signal engine"""
    print("=" * 80)
    print("ADVANCED SIGNAL ENGINE TEST")
    print("=" * 80)

    engine = AdvancedSignalEngine(min_confidence=65.0)

    # Test single symbol
    signal = engine.analyze_symbol("BTC_USDT", "gate.io")

    if signal:
        print("\n✅ SIGNAL GENERATED:")
        print(f"   Symbol: {signal.symbol}")
        print(f"   Direction: {signal.direction}")
        print(f"   Confidence: {signal.overall_confidence:.1f}%")
        print(f"   Entry: ${signal.entry_price:.2f}")
        print(f"   Stop Loss: ${signal.stop_loss:.2f}")
        print(f"   Take Profit: ${signal.take_profit:.2f}")
        print(f"   Position Size: ${signal.recommended_position_size:.2f}")
    else:
        print("\n❌ No signal generated")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_advanced_engine()
