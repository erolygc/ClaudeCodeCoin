# Phase 3: Risk Management System

## 🎯 Amaç
Sermaye koruması ve risk kontrolü ile sürdürülebilir trading.

## 📊 Ana Bileşenler

### 1. Position Sizing (position_sizing/)
**Ne Kadar Al/Sat?**

- **Fixed Fractional**: Her trade'de sermayenin %1-2'si
- **Kelly Criterion**: Matematiksel optimal pozisyon boyutu
- **Volatility-Based**: ATR bazlı pozisyon ayarlama
- **Risk Parity**: Tüm pozisyonlar eşit risk taşısın

```python
# Örnek: %2 risk ile pozisyon büyüklüğü
capital = 10000  # $10,000
risk_percent = 0.02  # %2
stop_loss_distance = 0.05  # %5

position_size = (capital * risk_percent) / stop_loss_distance
# = $400 / 0.05 = $8000 pozisyon
```

### 2. Stop Loss Management (stop_loss/)
**Kayıpları Sınırlama**

- **Fixed Stop Loss**: Sabit % stop
- **ATR-based Stop**: Volatilite bazlı
- **Trailing Stop**: Fiyatı takip eden stop
- **Time-based Stop**: Zaman limiti
- **Break-even Stop**: Maliyete çekme

### 3. Portfolio Risk (portfolio/)
**Toplam Portföy Riski**

- **Maximum Drawdown**: En fazla %15 kayıp
- **VAR (Value at Risk)**: %95 güvenle maksimum kayıp
- **Position Correlation**: Korelasyonlu pozisyonlardan kaçın
- **Sector/Asset Limits**: Her sectorden max %30

### 4. Correlation Analysis (correlation/)
**Asset Korelasyonu**

- Aynı yönde hareket eden coinlere aynı anda girme
- Negatif korelasyonlu coinlerle hedging
- Correlation matrix hesaplama

## 🎯 Risk Kuralları

```python
RISK_RULES = {
    'max_position_risk': 0.02,        # %2 per trade
    'max_portfolio_risk': 0.06,       # %6 total exposure
    'max_drawdown': 0.15,             # %15 max drawdown
    'max_leverage': 3,                # 3x max leverage
    'max_correlation': 0.7,           # 0.7 max correlation
    'max_positions': 10,              # 10 max open positions
    'min_risk_reward': 2.0,           # Min 1:2 risk/reward
}
```

## 📈 Kullanım

```python
from Phase3_RiskManagement import RiskManager

rm = RiskManager(capital=10000)

# Pozisyon büyüklüğü hesapla
position = rm.calculate_position_size(
    entry=100,
    stop_loss=95,  # %5 stop
    risk_percent=0.02  # %2 risk
)

# Risk check
if rm.can_open_position(position):
    # Open trade
    pass
else:
    print("Risk limit exceeded!")
```
