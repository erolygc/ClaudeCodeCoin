# ClaudeCodeCoin - Live Trading System Quick Start

## Overview

This system runs **live trading with real Gate.io API data** and **virtual money** (paper trading).

### System Components

1. **Gate.io Data Collector** - Collects real-time price data from 550 coins via WebSocket
2. **Pump Scanner** - Analyzes data in real-time to detect pump signals
3. **Paper Trading Engine** - Opens and closes virtual positions based on pump signals

---

## Quick Start (Windows)

### Option 1: One-Click Start (Recommended)

```batch
RUN_LIVE_SYSTEM_WINDOWS.bat
```

Then select:
- **[1]** - All in one window (simple, sequential logs)
- **[2]** - Separate windows (3 cmd windows for better monitoring)

### Option 2: Manual Start (Individual Components)

Open 3 separate CMD windows and run:

**Window 1: Data Collector**
```batch
python run_live_gateio_collector.py
```

**Window 2: Pump Scanner**
```batch
python run_live_pump_scanner.py
```

**Window 3: Paper Trading**
```batch
python run_live_paper_trading.py
```

---

## Quick Start (Linux/Mac)

### Option 1: Interactive Menu

```bash
chmod +x run_live_trading_system.sh
./run_live_trading_system.sh
```

Then select:
- **[1]** - Single terminal (simple)
- **[2]** - Separate terminals with tmux (advanced)
- **[3]** - Background processes (headless)

### Option 2: Manual Start

Open 3 terminals and run:

**Terminal 1: Data Collector**
```bash
python3 run_live_gateio_collector.py
```

**Terminal 2: Pump Scanner**
```bash
python3 run_live_pump_scanner.py
```

**Terminal 3: Paper Trading**
```bash
python3 run_live_paper_trading.py
```

---

## What Happens When Running?

### 1. Data Collector
- Connects to Gate.io WebSocket API
- Subscribes to 550 USDT trading pairs
- Receives 1-minute candlestick data in real-time
- Saves to `data_output/binance_data.db`

**Expected Output:**
```
🟢 GATE.IO COLLECTOR ACTIVE - Monitoring 550 coins
Saved 100 candles (Messages: 120)
Saved 200 candles (Messages: 245)
...
```

### 2. Pump Scanner
- Scans database every 60 seconds
- Analyzes 20 high-priority coins (configurable)
- Detects volume spikes, price surges, RSI patterns
- Saves pump alerts to `pump_alerts/pump_alerts_YYYYMMDD.json`

**Expected Output:**
```
[SCAN #1] 14:25:30
[PUMP DETECTED] PEPE_USDT - critical (92%)
  Price: +15.2%, Volume: 1250%
[SCAN #1] Found 1 pump signals
```

### 3. Paper Trading Engine
- Monitors pump alerts every 30 seconds
- Opens virtual positions with $10,000 starting balance
- Manages stop loss (5%) and take profit (10-25%)
- Logs all trades to database and console

**Expected Output:**
```
📊 PORTFÖY DURUMU
💰 Bakiye: $10,262.66
📈 Toplam P&L: $262.66 (+2.63%)
📊 Açık Pozisyon: 3
✅ Toplam İşlem: 7
🎯 Win Rate: 42.9%
```

---

## Configuration

### Production Mode Settings

File: `Phase7_PaperTrading/config.py`

```python
# Trading Parameters (PRODUCTION MODE)
MIN_CONFIDENCE_TO_TRADE = 70.0  # Minimum 70% confidence
MIN_VOLUME_SPIKE = 800.0        # Minimum 800% volume spike
STOP_LOSS_PERCENT = 5.0         # 5% stop loss
TAKE_PROFIT_PERCENT = {
    'CRITICAL': 25.0,  # 85%+ confidence
    'HIGH': 20.0,      # 70-85% confidence
    'MEDIUM': 15.0,    # 50-70% confidence
    'LOW': 10.0        # 30-50% confidence
}
```

### Test Mode (Lower Thresholds)

To test with more signals, edit `run_live_paper_trading.py`:

```python
# TEST MODE - More signals
config.MIN_CONFIDENCE_TO_TRADE = 50.0
config.MIN_VOLUME_SPIKE = 100.0
```

---

## Monitoring

### Real-Time Logs

**Windows:**
```batch
type logs\live_paper_trading.log
type logs\live_pump_scanner.log
```

**Linux/Mac:**
```bash
tail -f logs/live_paper_trading.log
tail -f logs/live_pump_scanner.log
```

### Database Inspection

```bash
python Phase1_DataBackbone/collectors/view_collected_data.py
```

### Performance Report

Paper trading engine prints portfolio summary every 10 iterations (~5 minutes).

---

## File Structure

```
ClaudeCodeCoin/
├── run_live_gateio_collector.py   # Real-time data collection
├── run_live_pump_scanner.py       # Pump detection
├── run_live_paper_trading.py      # Virtual trading
├── RUN_LIVE_SYSTEM_WINDOWS.bat    # Windows launcher
├── run_live_trading_system.sh     # Linux/Mac launcher
│
├── data_output/
│   └── binance_data.db            # Live price data
│
├── pump_alerts/
│   └── pump_alerts_20251109.json  # Detected pumps
│
├── logs/
│   ├── live_paper_trading.log     # Trading logs
│   ├── live_pump_scanner.log      # Scanner logs
│   └── gateio_collector_1000coins.log
│
└── Phase7_PaperTrading/
    ├── config.py                  # Trading parameters
    └── paper_trades.db            # Trade history
```

---

## Troubleshooting

### Gate.io Connection Issues

**Error:** `Cannot connect to api.gateio.ws`

**Solutions:**
1. Check internet connection
2. Verify Gate.io API is accessible in your region
3. Try with VPN if blocked
4. Use test data mode (see below)

### No Pump Signals Detected

**Reason:** Real markets may not have strong pumps at all times.

**Solutions:**
1. Lower thresholds in TEST MODE (see Configuration above)
2. Wait longer (pumps are rare in production)
3. Use simulated pump data for testing (see Testing section)

### Emoji Encoding Errors (Windows)

**Non-critical:** System works fine, just display issue.

**Fix:**
```batch
python fix_emoji_encoding.py
```

---

## Testing with Simulated Data

If you want to test the system without waiting for real pumps:

```bash
# 1. Generate test data with strong pumps
python generate_test_data.py
python generate_pump_data.py

# 2. Run pump scanner once
python run_pump_scan_once.py

# 3. Test paper trading (5 iterations)
python run_paper_trading_test.py
```

---

## Production Deployment

### Requirements

- Stable internet connection
- Minimum 2GB RAM
- Python 3.8+
- 24/7 server (VPS recommended for live trading)

### Recommended Setup

**Cloud VPS (DigitalOcean, AWS, etc.):**
```bash
# 1. Clone repository
git clone https://github.com/your-username/ClaudeCodeCoin.git
cd ClaudeCodeCoin

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run in background (tmux)
./run_live_trading_system.sh
# Select option [2] for tmux

# 4. Detach from tmux
Ctrl+B, then D

# 5. Monitor remotely
tmux attach -t claudecodecoin
```

---

## Performance Metrics

### Expected Results (Production Mode)

With **MIN_CONFIDENCE = 70%** and **MIN_VOLUME_SPIKE = 800%**:

- **Signals per day:** 2-10 (real pumps are rare)
- **Win rate target:** 40-60%
- **Average gain:** +5% to +15%
- **Max drawdown:** -5% (stop loss)

### Test Mode Results

With **MIN_CONFIDENCE = 50%** and **MIN_VOLUME_SPIKE = 100%**:

- **Signals per day:** 20-50 (more false positives)
- **Win rate:** 25-40%
- **For testing only, not production**

---

## Next Steps

1. **Monitor for 24 hours** - Observe system behavior with real data
2. **Analyze results** - Check `logs/live_paper_trading.log` for performance
3. **Optimize parameters** - Adjust confidence/volume thresholds based on results
4. **Scale up** - Increase monitored coins from 20 to 550
5. **Deploy to VPS** - Run 24/7 for continuous trading

---

## Support

For issues and questions:
- Check logs in `logs/` directory
- Review configuration in `Phase7_PaperTrading/config.py`
- Test with simulated data first

---

**WARNING:** This is paper trading (virtual money). No real trades are executed.
For live trading with real money, additional components are needed (see Phase 4: Order Execution).

---

## License

MIT License - See LICENSE file for details
