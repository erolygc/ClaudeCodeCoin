# Phase 2: Alpha Generation Engine

## 🎯 Amaç
Piyasadan alpha (fazla getiri) elde etmek için sistematik bir strateji geliştirme ve test ortamı.

## 📊 Ana Bileşenler

### 1. Indicators Library (indicators/)
**100+ Finansal İndikatör Kütüphanesi**

#### Trend Indicators:
- Moving Averages: SMA, EMA, WMA, HMA, TEMA, DEMA
- MACD (Moving Average Convergence Divergence)
- ADX (Average Directional Index)
- Parabolic SAR
- Ichimoku Cloud
- Supertrend

#### Momentum Indicators:
- RSI (Relative Strength Index)
- Stochastic Oscillator (%K, %D)
- Williams %R
- CCI (Commodity Channel Index)
- MFI (Money Flow Index)
- ROC (Rate of Change)
- TSI (True Strength Index)

#### Volatility Indicators:
- Bollinger Bands
- ATR (Average True Range)
- Keltner Channels
- Donchian Channels
- Standard Deviation
- Historical Volatility

#### Volume Indicators:
- OBV (On-Balance Volume)
- VWAP (Volume Weighted Average Price)
- Accumulation/Distribution
- Chaikin Money Flow
- Volume Profile
- VPVR (Volume Profile Visible Range)

#### Pattern Recognition:
- Candlestick Patterns (50+ patterns)
- Chart Patterns (Head & Shoulders, Triangles, etc.)
- Support/Resistance Levels
- Fibonacci Retracements

#### Market Breadth:
- Advance/Decline Ratio
- McClellan Oscillator
- Trin (Arms Index)

#### Custom/Synthetic:
- Indicator Combinations
- Machine Learning Features
- Wavelet Transforms
- Fourier Analysis

---

### 2. Feature Engineering (features/)
**İndikatör kombinasyonları ve synthetic features**

- Cross-indicator signals
- Normalized features
- Time-series transformations
- Statistical aggregations
- Correlation-based features

---

### 3. DVK - Dynamic Asset Characterization (dvk/)
**Her coin için hangi indikatörlerin işe yaradığını öğrenme**

- Indicator effectiveness scoring
- Coin personality profiling
- Adaptive strategy selection
- Market regime detection

**Örnek:**
- BTC: Trend-following indicators (SMA, MACD) etkili
- ETH: Momentum indicators (RSI, Stochastic) daha iyi
- Altcoinler: Volume indicators önemli

---

### 4. Backtesting Framework (backtesting/)
**Stratejileri geçmiş verilerde test etme**

- Historical data replay
- Performance metrics (Sharpe, Sortino, Max DD)
- Transaction cost simulation
- Slippage modeling
- Walk-forward analysis
- Monte Carlo simulation

---

### 5. Strategy Generator (strategies/)
**Otomatik strateji oluşturma ve optimizasyon**

- Rule-based strategies
- Indicator combination strategies
- Threshold optimization
- Parameter grid search

---

### 6. Genetic Programming (genetic_programming/)
**Evrimsel algoritma ile strateji evrim**

- Strategy DNA encoding
- Fitness evaluation (Sharpe ratio)
- Crossover & Mutation operations
- Population evolution
- Elite selection

**Nasıl Çalışır:**
1. Rastgele 100 strateji oluştur
2. Backtesting ile fitness hesapla
3. En iyi 20 stratejiyi seç
4. Crossover (çaprazlama) ve mutasyon uygula
5. Yeni nesil oluştur
6. 100+ nesil boyunca evrim devam et
7. En iyi stratejileri bul

---

## 🎯 Hedef Çıktılar

1. **Strategy Library**: 1000+ test edilmiş strateji
2. **DVK Profiles**: Her coin için kişilik profili
3. **Performance Database**: Tüm stratejilerin performansı
4. **Adaptive System**: Piyasa koşullarına göre strateji değiştirme

---

## 📈 Başarı Metrikleri

- **Sharpe Ratio** > 2.0
- **Max Drawdown** < 15%
- **Win Rate** > 60%
- **Profit Factor** > 2.0
- **Sortino Ratio** > 3.0

---

## 🚀 Kullanım

```python
from Phase2_AlphaEngine.indicators import AdvancedIndicators
from Phase2_AlphaEngine.backtesting import Backtester
from Phase2_AlphaEngine.dvk import DVKEngine
from Phase2_AlphaEngine.genetic_programming import StrategyEvolution

# 1. İndikatörleri hesapla
indicators = AdvancedIndicators()
indicators.calculate_all(symbol="BTCUSDT")

# 2. Strateji oluştur
strategy = {
    'entry': 'RSI < 30 AND MACD_cross_up',
    'exit': 'RSI > 70 OR stop_loss',
    'position_size': '2%'
}

# 3. Backtest çalıştır
backtester = Backtester()
results = backtester.run(strategy, start_date='2024-01-01', end_date='2024-12-31')

# 4. DVK ile optimize et
dvk = DVKEngine()
best_indicators = dvk.find_best_indicators(symbol="BTCUSDT")

# 5. Genetik algoritma ile evrim
evolution = StrategyEvolution(population_size=100, generations=50)
best_strategy = evolution.evolve()
```

---

## 📁 Dosya Yapısı

```
Phase2_AlphaEngine/
├── indicators/
│   ├── trend.py           # Trend indikatörleri
│   ├── momentum.py        # Momentum indikatörleri
│   ├── volatility.py      # Volatilite indikatörleri
│   ├── volume.py          # Volume indikatörleri
│   ├── patterns.py        # Pattern recognition
│   └── advanced.py        # Gelişmiş/custom indikatörler
│
├── features/
│   ├── engineering.py     # Feature engineering
│   ├── normalization.py   # Feature normalization
│   └── selection.py       # Feature selection
│
├── backtesting/
│   ├── engine.py          # Backtesting engine
│   ├── metrics.py         # Performance metrics
│   ├── simulation.py      # Trade simulation
│   └── reports.py         # Report generation
│
├── dvk/
│   ├── analyzer.py        # Coin personality analyzer
│   ├── scorer.py          # Indicator effectiveness scorer
│   └── regime.py          # Market regime detector
│
├── strategies/
│   ├── rules.py           # Rule-based strategies
│   ├── combinations.py    # Indicator combinations
│   └── optimizer.py       # Parameter optimizer
│
└── genetic_programming/
    ├── dna.py             # Strategy DNA encoding
    ├── evolution.py       # Evolution engine
    ├── fitness.py         # Fitness evaluation
    └── operators.py       # Genetic operators
```

---

## 🔜 Sonraki Adımlar

1. Indicators library'yi genişlet (100+ indicator)
2. Backtesting engine'i oluştur
3. DVK sistemini implement et
4. Genetik algoritma ile strateji evrim

**Estimated Time:** 2-3 gün yoğun çalışma
