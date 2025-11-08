# 🪟 Multi-Window Trading System Guide

## 📋 Overview

The multi-window mode launches each component of the trading system in a **separate terminal window**, making it easier to monitor and debug each service independently.

---

## ✨ Benefits

✅ **Better Monitoring** - See each component's output separately
✅ **Easier Debugging** - Identify which service has issues
✅ **Independent Control** - Stop/restart individual components
✅ **Cleaner Output** - No mixed log messages
✅ **Multi-Screen Support** - Position windows on different monitors

---

## 🚀 Quick Start

### **Windows**

#### **Method 1: Batch File (Recommended)**

```powershell
.\START_SYSTEM_MULTIWINDOW.bat
```

Double-click the file in Explorer!

#### **Method 2: Python**

```powershell
python start_system_multiwindow.py
```

### **Linux/Mac**

```bash
python start_system_multiwindow.py
```

Requires: `gnome-terminal`, `xterm`, `konsole`, or `xfce4-terminal`

---

## 🪟 Window Layout

When you start the system, you'll see **3 windows**:

### **Window 1: Master Controller**

```
┌─────────────────────────────────────────────────────────────┐
│ CLAUDECODECOIN - MULTI-WINDOW TRADING SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ✅ ALL COMPONENTS LAUNCHED IN SEPARATE WINDOWS              │
│                                                              │
│ You should now see:                                          │
│   1️⃣  Window: Hybrid Scanner                               │
│   2️⃣  Window: Paper Trading Engine                         │
│                                                              │
│ 📊 Monitor:                                                  │
│    - Logs: logs/                                             │
│    - Signals: Phase6_PumpDetection/signals/                  │
│    - Performance: paper_trading_performance.db               │
│                                                              │
│ 💡 Quick monitoring commands:                                │
│    .\watch_logs.ps1 logs\paper_trading.log                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Purpose:** Shows system status and monitoring instructions
**Action:** Can be closed after reading (doesn't affect other windows)

### **Window 2: Hybrid Scanner**

```
┌─────────────────────────────────────────────────────────────┐
│ HYBRID PUMP SCANNER                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 🔍 Starting scan cycle...                                    │
│ 📊 Analyzing 50 symbols across 7 timeframes...               │
│                                                              │
│ ✅ BTC_USDT - Pump Score: 65.4% (Confidence: 72.3%)          │
│ ✅ ETH_USDT - Pump Score: 58.2% (Confidence: 68.1%)          │
│                                                              │
│ 💾 Saved signal: hybrid_BTC_USDT_20250108_143052.json        │
│                                                              │
│ ⏳ Next scan in 30 seconds...                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Purpose:** Real-time pump detection and signal generation
**Output:** Pump scores, confidence levels, generated signals
**Action:** Keep open to monitor scanning activity

### **Window 3: Paper Trading Engine**

```
┌─────────────────────────────────────────────────────────────┐
│ PAPER TRADING ENGINE                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 💰 Initial Balance: $10,000.00                               │
│                                                              │
│ 📊 New signal detected: BTC_USDT                             │
│ ✅ Opened LONG position:                                     │
│    Entry: $43,250.00                                         │
│    Size: $100.00                                             │
│    Stop Loss: $42,815.00 (-1.0%)                             │
│    Take Profit: $44,595.00 (+3.1%)                           │
│                                                              │
│ ================================================================================│
│ ACCOUNT STATISTICS                                           │
│ ================================================================================│
│ Balance: $10,156.20                                          │
│ Open Positions: 3/10                                         │
│ Win Rate: 75.0%                                              │
│ ================================================================================│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Purpose:** Automated position management and performance tracking
**Output:** Trade executions, account stats, PnL updates
**Action:** Keep open to monitor trading activity

---

## 🎮 Usage Examples

### **Example 1: Default (Top 50 Coins)**

```powershell
.\START_SYSTEM_MULTIWINDOW.bat
```

- Scans top 50 Gate.io futures contracts
- Recommended for diversification

### **Example 2: Specific Coins**

```powershell
python start_system_multiwindow.py --coins BTC_USDT,ETH_USDT,SOL_USDT,BNB_USDT
```

- Only scans specified coins
- More focused, faster scanning

### **Example 3: Top 20 Only**

```powershell
python start_system_multiwindow.py --top 20
```

- Scans top 20 by volume
- Balance between speed and coverage

---

## 🛑 Stopping the System

### **Option 1: Individual Windows**

Press `Ctrl+C` in each window to stop that component:

1. Stop Scanner → Ctrl+C in Scanner window
2. Stop Trading Engine → Ctrl+C in Trading Engine window
3. Close Master Controller → X button

### **Option 2: Close Windows**

Simply close each terminal window with the X button.

### **Option 3: Kill All Processes (Windows)**

```powershell
Stop-Process -Name python -Force
```

This stops all Python processes (use with caution if running other Python scripts).

### **Option 4: Kill All Processes (Linux)**

```bash
pkill -f "start_system_multiwindow"
pkill -f "realtime_hybrid_scanner"
pkill -f "paper_trading_futures_engine"
```

---

## 📊 Monitoring & Debugging

### **Real-Time Log Monitoring**

Open **additional windows** to watch logs:

#### **Watch Trading Logs (PowerShell)**

```powershell
.\watch_logs.ps1 logs\paper_trading.log
```

#### **Watch Scanner Logs (PowerShell)**

```powershell
.\watch_logs.ps1 logs\realtime_hybrid_scanner.log
```

#### **Manual Tail (PowerShell)**

```powershell
Get-Content logs\paper_trading.log -Wait -Tail 20
```

#### **Linux/Mac**

```bash
tail -f logs/paper_trading.log
tail -f logs/realtime_hybrid_scanner.log
```

### **View Generated Signals**

```powershell
# List all signals
dir Phase6_PumpDetection\signals\

# View latest signal
Get-Content (Get-ChildItem Phase6_PumpDetection\signals\*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | ConvertFrom-Json | ConvertTo-Json
```

### **Query Performance Database**

```powershell
# Last 10 trades
sqlite3 paper_trading_performance.db "SELECT symbol, direction, pnl, pnl_percent FROM positions WHERE status='CLOSED' ORDER BY closed_at DESC LIMIT 10"

# Win rate
sqlite3 paper_trading_performance.db "SELECT COUNT(*) as total, SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins, ROUND(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as win_rate FROM positions WHERE status='CLOSED'"

# Account summary
sqlite3 paper_trading_performance.db "SELECT * FROM account_snapshots ORDER BY timestamp DESC LIMIT 1"
```

---

## 🔧 Troubleshooting

### **Problem: Windows don't open**

**Cause:** `cmd.exe` not in PATH

**Solution:**
```powershell
# Use full path
C:\Windows\System32\cmd.exe /k run_scanner.bat
```

### **Problem: Scanner window closes immediately**

**Cause:** Error in scanner script or missing dependencies

**Solution:**
```powershell
# Run directly to see error
python Phase6_PumpDetection\realtime_hybrid_scanner.py --interval 30
```

### **Problem: Trading engine not detecting signals**

**Cause:** Signal directory doesn't exist or scanner hasn't run

**Solution:**
```powershell
# Check signal directory
dir Phase6_PumpDetection\signals\

# Create if missing
mkdir Phase6_PumpDetection\signals
```

### **Problem: All windows on one monitor**

**Solution:** Manually position windows on different monitors after launch.

---

## ⚙️ Customization

### **Change Window Titles**

Edit `run_scanner.bat`:

```batch
title My Custom Scanner Name
```

Edit `run_trading_engine.bat`:

```batch
title My Custom Trading Engine
```

### **Change Window Size (PowerShell)**

```powershell
# Set console buffer size
mode con: cols=120 lines=40
```

### **Auto-Position Windows (Advanced)**

Use PowerShell to position windows:

```powershell
# Requires PowerShell 5.1+
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@
```

---

## 📁 File Structure

```
ClaudeCodeCoin/
├── START_SYSTEM_MULTIWINDOW.bat          ← Main launcher (Windows)
├── start_system_multiwindow.py           ← Main launcher (Cross-platform)
├── run_scanner.bat                       ← Scanner wrapper (Windows)
├── run_trading_engine.bat                ← Trading engine wrapper (Windows)
│
├── logs/
│   ├── paper_trading.log                 ← Trading logs
│   └── realtime_hybrid_scanner.log       ← Scanner logs
│
├── Phase6_PumpDetection/signals/         ← Generated signals
│   └── hybrid_*.json
│
└── paper_trading_performance.db          ← Performance database
```

---

## 💡 Pro Tips

### **1. Multi-Monitor Setup**

Position windows for optimal monitoring:

- **Monitor 1:** Scanner + Trading Engine windows
- **Monitor 2:** Log monitoring (watch_logs.ps1)
- **Monitor 3:** Database queries (sqlite3)

### **2. Color-Code Windows**

Use different color schemes for each window:

```powershell
# In each window
color 0A  # Green on black (Scanner)
color 0B  # Cyan on black (Trading)
color 0E  # Yellow on black (Logs)
```

### **3. Save Window Layout**

Use Windows Terminal (modern alternative):

1. Install Windows Terminal from Microsoft Store
2. Create profile for each component
3. Save layout

### **4. Automated Screenshots**

Monitor system visually:

```powershell
# Take screenshot every 5 minutes
while ($true) {
    Add-Type -AssemblyName System.Windows.Forms
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
    $bitmap.Save("screenshots\$(Get-Date -Format 'yyyyMMdd_HHmmss').png")
    Start-Sleep -Seconds 300
}
```

---

## 🆚 Multi-Window vs Single-Window

| Feature | Multi-Window | Single-Window |
|---------|--------------|---------------|
| Monitoring | ⭐⭐⭐⭐⭐ Each component clear | ⭐⭐⭐ Mixed output |
| Debugging | ⭐⭐⭐⭐⭐ Easy to isolate issues | ⭐⭐⭐ Harder to find errors |
| Resource | ⭐⭐⭐ More terminal windows | ⭐⭐⭐⭐⭐ Single window |
| Control | ⭐⭐⭐⭐⭐ Stop/restart individual | ⭐⭐⭐ All or nothing |
| Setup | ⭐⭐⭐⭐ Double-click launch | ⭐⭐⭐⭐⭐ Simplest |

**Recommendation:** Use **Multi-Window** for active monitoring and debugging.

---

## 🚀 Next Steps

1. ✅ Launch system with `START_SYSTEM_MULTIWINDOW.bat`
2. ✅ Position windows for optimal viewing
3. ✅ Open log monitoring in separate window
4. ✅ Watch for signals and trades
5. ✅ Analyze performance after 1 hour
6. ✅ Adjust parameters if needed

---

## 📞 Support

- **Main Guide:** `TRADING_SYSTEM_QUICKSTART.md`
- **Windows Guide:** `WINDOWS_QUICKSTART.md`
- **Configuration:** `config/paper_trading_config.py`

---

**Happy Multi-Window Trading! 🚀📊**

*Remember: This is paper trading with virtual money. No real financial risk.*
