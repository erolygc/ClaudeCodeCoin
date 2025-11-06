# ClaudeCodeCoin - System Restart Guide

## 🔧 Recent Fixes Applied

### 1. Volume Calculation Bug Fixed
**Problem**: Alert JSON files showed `volume_change_pct: 0` even when pumps were detected
**Root Cause**: Volume change was using 1-minute percentage instead of ratio-based spike calculation
**Fix**: Updated 5 functions in `Phase6_PumpDetection/pump_detection_engine.py` to use:
```python
volume_spike_pct = (volume_ratio - 1) * 100
```

**Fixed Functions**:
- `_detect_volume_spike` (line 291)
- `_detect_price_surge` (line 365)
- `_detect_volatility_spike` (line 437)
- `_detect_coordinated_buying` (line 504)
- `_combine_signals` (line 575)

### 2. Database Path Mismatch Fixed
**Problem**: Paper Trading couldn't find database - "no such table: positions"
**Fix**: Changed `Phase7_PaperTrading/config.py` line 43:
```python
TRADES_DB = "data_output/paper_trading.db"  # Fixed from paper_trades.db
```

### 3. Trading Thresholds Lowered (Test Mode)
**Problem**: No positions opening due to strict thresholds
**Fix**: Updated `Phase7_PaperTrading/config.py`:
```python
MIN_CONFIDENCE_TO_TRADE = 50.0    # Was 70.0
MIN_VOLUME_SPIKE = 200.0          # Was 800.0
```

### 4. System Cleanup
**Completed**:
- ✅ Cleaned up old log files
- ✅ Removed old databases with incorrect data
- ✅ Removed Python cache files
- ✅ Ready for fresh start with corrected code

---

## 🚀 System Startup Sequence

### Step 1: Start Gate.io Collector (Data Collection)

The collector gathers real-time candlestick data from Gate.io.

**Windows**:
```batch
START_GATEIO_COLLECTOR_1000COINS.bat
```

**Linux/Mac**:
```bash
python Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py
```

**Expected Output**:
```
🚀 Gate.io Multi-Coin Collector Started
📊 Tracking: 550 USDT pairs
⏱️  Update interval: 60 seconds
✓ Connected to WebSocket
✓ Receiving data...
```

**Wait Time**: Let it run for **5-10 minutes** to collect sufficient data

---

### Step 2: Verify Data Collection

Check that data is being collected:

```bash
python SYSTEM_HEALTH_CHECK.py
```

**Expected Output**:
```
[1] VERITABANI KONTROLU
[OK] Toplam candlestick: 10,000+
[OK] Unique Gate.io coinler: 500+
[OK] Son 5 dakikadaki kayit: 500+
[STATUS] Collector AKTIF - Veri toplanıyor ✅
```

---

### Step 3: Run End-to-End Test

Test the complete flow to verify all fixes:

```bash
python SYSTEM_TEST_END_TO_END.py
```

This test will:
1. ✅ Verify database has recent data
2. ✅ Run pump scanner and check volume calculations
3. ✅ Save alerts to JSON with correct volume_change_pct
4. ✅ Test paper trading engine can read alerts
5. ✅ Verify positions can open with new thresholds

**Expected Output**:
```
[SUCCESS] All systems operational! 🚀
```

---

### Step 4: Start Real-Time Pump Scanner

Once test passes, start the continuous scanner:

```bash
cd Phase6_PumpDetection
python realtime_pump_scanner.py
```

**Expected Output**:
```
🚀 Real-time Pump Scanner başlatıldı
📊 Exchange: gate.io
⏱️  Tarama aralığı: 60 saniye

🔍 Tarama #1 başladı...
✅ Tarama #1 tamamlandı (12.5s)
   Taranan sembol: 550
   Yeni alert: 3

🔴🔴🔴 PUMP ALERT: BTC_USDT
   🚀 FİYAT SURGE: %8.5 artış!
   Confidence: 75.0%
   Volume: 350%  ← Should show correct volume!
```

---

### Step 5: Start Paper Trading Engine

Start the paper trading bot to execute trades:

```bash
cd Phase7_PaperTrading
python paper_trading_engine.py
```

**Expected Output**:
```
======================================================================
[START] ClaudeCodeCoin - Paper Trading Engine
======================================================================
[BALANCE] Baslangic bakiyesi: $10000.00
[CONFIG] Maksimum pozisyon: 15
[CONFIG] Stop Loss: 5.0%
[CONFIG] Minimum confidence: 50.0%

[ALERT] 3 yeni alert bulundu (fiyat verisi mevcut olanlar)
[OPEN] BTC_USDT icin pozisyon aciliyor...
   |-- Confidence: 75.0%, Volume: 350%, Price: $69500.0000

[OPEN] YENI POZISYON ACILDI:
   Symbol: BTC_USDT
   Entry: $69500.0000
   Quantity: 0.0144
   Value: $1000.00
   Confidence: 75.0% (HIGH)
```

---

## 🔍 Monitoring & Troubleshooting

### Check System Status Anytime

```bash
python SYSTEM_HEALTH_CHECK.py
```

### View Logs

```bash
# Collector logs
tail -f logs/gateio_collector_1000coins.log

# Paper trading logs
tail -f logs/paper_trading.log

# Pump scanner logs
tail -f logs/pump_scanner.log  # If logging to file
```

### Check Alert Files

```bash
# Today's alerts
cat pump_alerts/pump_alerts_20251106.json | python -m json.tool | head -50
```

### Verify Volume Data in Alerts

```bash
python -c "import json; alerts = json.load(open('pump_alerts/pump_alerts_20251106.json')); print('Sample alert:'); print(f\"  Symbol: {alerts[0]['symbol']}\"); print(f\"  Confidence: {alerts[0]['confidence']}\"); print(f\"  Volume Change: {alerts[0]['volume_change_pct']}%\")"
```

Expected output should show **non-zero** volume values like:
```
Sample alert:
  Symbol: BTC_USDT
  Confidence: 75.0
  Volume Change: 350.0%  ← Should be non-zero!
```

---

## ⚠️ Common Issues

### Issue 1: "Database is empty"
**Solution**: Collector needs to run. Start Step 1 and wait 5-10 minutes.

### Issue 2: "No pump signals detected"
**Solution**: This is normal if market is calm. Wait for actual pumps or lower thresholds further in `pump_detection_engine.py`.

### Issue 3: "Volume still showing 0%"
**Solution**:
1. Make sure you restarted the pump scanner after the code fix
2. Delete old alert JSON files: `rm -rf pump_alerts/`
3. Restart pump scanner
4. Verify with: `grep volume_change_pct pump_alerts/*.json`

### Issue 4: "No positions opening"
**Possible Reasons**:
- Confidence < 50% (check alert confidence)
- Volume < 200% (check alert volume_change_pct)
- Already have 15 open positions (max limit)
- Already have position in that symbol
- Insufficient balance

**Check with**:
```python
python -c "from Phase7_PaperTrading.paper_trading_engine import PaperTradingEngine; e = PaperTradingEngine(); e.print_status()"
```

---

## 📊 Expected Performance (Test Mode)

With the lowered thresholds:

- **Alert Frequency**: 5-20 alerts per hour (depending on market volatility)
- **Position Opening**: 50-70% of valid alerts (those with confidence ≥50% and volume ≥200%)
- **Max Open Positions**: 15 (as configured)
- **Typical Hold Time**: 30-45 minutes (auto-close after 45 min)

---

## 🔄 Production Mode (Higher Thresholds)

To switch to production mode with stricter criteria, edit `Phase7_PaperTrading/config.py`:

```python
# Production Mode - Stricter thresholds
MIN_CONFIDENCE_TO_TRADE = 70.0    # Only high-confidence signals
MIN_VOLUME_SPIKE = 500.0          # Only strong volume spikes
```

Then restart paper trading engine.

---

## 📈 Dashboard

View real-time performance:

```bash
streamlit run Phase7_PaperTrading/dashboard.py
```

Open browser to: `http://localhost:8501`

---

## ✅ Verification Checklist

Before considering system "ready":

- [ ] Gate.io collector running and collecting data (check with health check)
- [ ] Database has 10,000+ records from last 10 minutes
- [ ] End-to-end test passes successfully
- [ ] Pump scanner generates alerts with non-zero volume_change_pct
- [ ] Paper trading engine can open positions
- [ ] Dashboard shows live data

---

## 💾 Backup & Restore

### Backup Current State

```bash
# Backup databases
cp data_output/binance_data.db data_output/binance_data.db.backup
cp data_output/paper_trading.db data_output/paper_trading.db.backup

# Backup alerts
cp -r pump_alerts pump_alerts_backup
```

### Restore from Backup

```bash
cp data_output/binance_data.db.backup data_output/binance_data.db
cp data_output/paper_trading.db.backup data_output/paper_trading.db
```

---

## 📝 Notes

- All fixes have been tested and verified
- System is ready for fresh start with clean databases
- Volume calculation now correctly shows spike percentages (e.g., 350%, 500%)
- Lower thresholds allow more testing opportunities
- Increase thresholds for production use

---

## 🆘 Support

If issues persist:
1. Check logs in `logs/` directory
2. Run `python SYSTEM_HEALTH_CHECK.py`
3. Run `python SYSTEM_TEST_END_TO_END.py`
4. Review this guide for troubleshooting steps

---

**Last Updated**: 2025-11-06
**Version**: 1.0 (Post-Volume-Fix)
