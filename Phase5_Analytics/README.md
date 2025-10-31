# Phase 5: Performance Analytics & Feedback Loop

## 🎯 Amaç
Performans izleme, raporlama ve sistemin sürekli iyileştirilmesi.

## 📊 Ana Bileşenler

### 1. Performance Metrics (metrics/)
**Performans Metrikleri**

#### Returns:
- **Total Return**: Toplam getiri %
- **Annual Return**: Yıllık getiri %
- **Monthly Returns**: Aylık dağılım

#### Risk Metrics:
- **Sharpe Ratio**: Risk-adjusted return (>2.0 hedef)
- **Sortino Ratio**: Downside risk odaklı (>3.0 hedef)
- **Max Drawdown**: En büyük düşüş (<%15 hedef)
- **Calmar Ratio**: Return / Max DD

#### Trade Metrics:
- **Win Rate**: Kazanan trade % (>60% hedef)
- **Profit Factor**: Gross Profit / Gross Loss (>2.0 hedef)
- **Average Win/Loss**: Ortalama kazanç/kayıp
- **Expectancy**: Trade başına beklenen kazanç

### 2. Strategy Tracking (tracking/)
**Strateji Takibi**

Her stratejinin performansını ayrı ayrı izle:

```python
{
    'strategy_id': 'RSI_MACD_v1',
    'total_trades': 150,
    'win_rate': 0.65,
    'sharpe_ratio': 2.4,
    'max_drawdown': 0.12,
    'total_return': 0.45,  # %45
    'status': 'active'  # active/paused/archived
}
```

### 3. Feedback Loop (feedback/)
**Öğrenme ve İyileştirme**

- **Strategy Selection**: En iyi performans gösteren stratejileri daha fazla kullan
- **Parameter Adaptation**: Piyasa koşullarına göre parametreleri ayarla
- **Market Regime Detection**: Bull/bear/sideways tespiti
- **Auto-disable**: Kötü performans gösteren stratejileri durdur

### 4. Reporting & Alerts (reporting/, alerts/)
**Raporlama ve Uyarılar**

#### Daily Report:
```
📊 Daily Performance Report
Date: 2025-10-31

💰 P&L: +$1,250 (+12.5%)
📈 Trades: 15 (10W / 5L)
🎯 Win Rate: 66.7%
📊 Sharpe: 2.8
⚠️  Max DD: -8.2%

Top Strategy: RSI_MACD_v1 (+$850)
Worst Strategy: BB_Mean_Reversion (-$200)
```

#### Alerts:
- Slack/Email notifications
- Max drawdown exceeded
- Strategy stopped due to poor performance
- New high achieved

## 🎯 Feedback Loop Akışı

```
1. Collect Performance Data
   ↓
2. Calculate Metrics
   ↓
3. Analyze Strategy Performance
   ↓
4. Identify Best/Worst Performers
   ↓
5. Adjust Allocation
   ↓
6. Disable Poor Performers
   ↓
7. Generate Report
   ↓
8. Send Alerts
   ↓
9. Archive Data
   ↓
10. Repeat Daily
```

## 📈 Kullanım

```python
from Phase5_Analytics import PerformanceTracker, FeedbackLoop

# Performance tracking
tracker = PerformanceTracker()
metrics = tracker.calculate_metrics(
    trades=trade_history,
    capital=initial_capital
)

print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Win Rate: {metrics['win_rate']:.1%}")

# Feedback loop
feedback = FeedbackLoop()
adjustments = feedback.analyze_and_adjust(
    strategy_performance=strategy_results
)

# Generate report
report = tracker.generate_daily_report()
report.send_to_slack()
```

## 🎯 Başarı Kriterleri

```python
SUCCESS_CRITERIA = {
    'sharpe_ratio': 2.0,      # Min 2.0
    'max_drawdown': 0.15,     # Max %15
    'win_rate': 0.60,         # Min %60
    'profit_factor': 2.0,     # Min 2.0
    'sortino_ratio': 3.0,     # Min 3.0
    'calmar_ratio': 3.0,      # Min 3.0
}
```

## 📊 Dashboard

Grafana/Plotly ile real-time dashboard:
- Equity curve
- Drawdown chart
- Win/loss distribution
- Strategy comparison
- Monthly heatmap
