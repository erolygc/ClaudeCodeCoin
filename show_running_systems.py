#!/usr/bin/env python3
"""
ClaudeCodeCoin - Show Running Systems
Displays all running trading system components
"""

import psutil
import sys
from datetime import datetime
import requests


def format_bytes(bytes_value):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"


def format_time(seconds):
    """Format seconds to human-readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def check_dashboard():
    """Check if dashboard is accessible"""
    try:
        response = requests.get("http://localhost:8501", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    print()
    print("=" * 80)
    print(" CLAUDECODECOIN - RUNNING SYSTEMS")
    print("=" * 80)
    print()

    # Find all Python processes
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
        try:
            if 'python' in proc.info['name'].lower():
                python_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if python_processes:
        print("🐍 Python Processes:")
        print()

        for proc in python_processes:
            try:
                pid = proc.info['pid']
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                memory = proc.info['memory_info'].rss
                cpu = proc.cpu_percent(interval=0.1)
                create_time = datetime.fromtimestamp(proc.info['create_time'])
                runtime = datetime.now() - create_time

                # Identify component
                component = "Unknown"
                icon = "❓"
                color_code = ""

                if 'realtime_hybrid_scanner' in cmdline:
                    component = "Hybrid Scanner"
                    icon = "🔍"
                    color_code = "\033[93m"  # Yellow
                elif 'paper_trading_futures_engine' in cmdline:
                    component = "Paper Trading Engine"
                    icon = "💰"
                    color_code = "\033[92m"  # Green
                elif 'streamlit' in cmdline or 'dashboard' in cmdline:
                    component = "Trading Dashboard"
                    icon = "📊"
                    color_code = "\033[95m"  # Magenta
                else:
                    component = "Other Python Process"
                    color_code = "\033[90m"  # Gray

                reset_code = "\033[0m"

                print(f"  {icon} {color_code}{component}{reset_code}")
                print(f"     PID: {pid}")
                print(f"     Started: {create_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"     Runtime: {format_time(runtime.total_seconds())}")
                print(f"     CPU: {cpu:.1f}%")
                print(f"     Memory: {format_bytes(memory)}")
                print(f"     Command: {cmdline[:100]}...")
                print()

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        print(f"Total Python Processes: {len(python_processes)}")
    else:
        print("❌ No Python processes running")

    print()
    print("=" * 80)
    print(" DASHBOARD STATUS")
    print("=" * 80)
    print()

    if check_dashboard():
        print("✅ Dashboard is RUNNING at http://localhost:8501")
    else:
        print("❌ Dashboard is NOT accessible")

    print()
    print("=" * 80)
    print(" QUICK ACTIONS")
    print("=" * 80)
    print()

    print("Stop all components:")
    if sys.platform == 'win32':
        print("  Stop-Process -Name python -Force")
    else:
        print("  pkill -f 'python.*scanner'")
        print("  pkill -f 'python.*trading'")
        print("  pkill -f 'streamlit'")

    print()
    print("Watch logs:")
    if sys.platform == 'win32':
        print("  .\\watch_logs.ps1 logs\\paper_trading.log")
    else:
        print("  tail -f logs/paper_trading.log")

    print()
    print("Open dashboard:")
    if sys.platform == 'win32':
        print("  start http://localhost:8501")
    else:
        print("  xdg-open http://localhost:8501")

    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
