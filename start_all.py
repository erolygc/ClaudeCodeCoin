"""
ClaudeCodeCoin - Master Başlatma Scripti
Tüm sistemi tek komutla başlatır:
  1. Gate.io Data Collector (550 coins)
  2. Pump Detection Scanner
  3. Paper Trading Engine
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
from datetime import datetime

# Platform kontrolü
IS_WINDOWS = sys.platform.startswith('win')

class ClaudeCodeCoinMaster:
    """Tüm sistem componentlerini yöneten master class"""

    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent

    def print_banner(self):
        """Başlangıç banner'ı"""
        print("\n" + "="*80)
        print(" " * 20 + "CLAUDECODECOIN - MASTER LAUNCHER")
        print("="*80)
        print(f" Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Platform: {'Windows' if IS_WINDOWS else 'Linux/Mac'}")
        print("="*80)
        print("\n[INFO] 3 Component baslatiliyor:")
        print("  [1] Gate.io Data Collector (550 coins)")
        print("  [2] Realtime Pump Scanner")
        print("  [3] Paper Trading Engine")
        print("\n[CTRL+C] Tum sistemi durdurmak icin: Ctrl+C")
        print("="*80 + "\n")

    def start_component(self, name, script_path, component_num):
        """Bir component'i başlat"""
        print(f"[{component_num}/3] {name} baslatiliyor...")

        try:
            if IS_WINDOWS:
                # Windows: CREATE_NEW_CONSOLE ile yeni pencere
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    cwd=str(self.project_root),
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # Linux/Mac: xterm veya gnome-terminal ile yeni terminal
                # Eğer GUI yoksa normal subprocess
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            self.processes.append({
                'name': name,
                'process': process,
                'path': script_path
            })

            time.sleep(2)  # Component'in başlaması için bekle

            # Process hala çalışıyor mu kontrol et
            if process.poll() is None:
                print(f"[OK] {name} baslatildi (PID: {process.pid})")
                return True
            else:
                print(f"[ERROR] {name} baslatma hatasi!")
                stdout, stderr = process.communicate()
                if stderr:
                    print(f"  Hata: {stderr.decode()[:200]}")
                return False

        except Exception as e:
            print(f"[ERROR] {name} baslatma hatasi: {e}")
            return False

    def start_all(self):
        """Tüm componentleri başlat"""
        self.print_banner()

        components = [
            {
                'name': 'Gate.io Collector',
                'path': 'Phase1_DataBackbone/collectors/multi_coin_gateio_collector_1000coins.py',
                'num': 1
            },
            {
                'name': 'Pump Scanner',
                'path': 'Phase6_PumpDetection/realtime_pump_scanner.py',
                'num': 2
            },
            {
                'name': 'Paper Trading',
                'path': 'Phase7_PaperTrading/paper_trading_engine.py',
                'num': 3
            }
        ]

        success_count = 0

        for component in components:
            script_path = self.project_root / component['path']

            if not script_path.exists():
                print(f"[ERROR] {component['name']} bulunamadi: {script_path}")
                continue

            if self.start_component(component['name'], script_path, component['num']):
                success_count += 1

            time.sleep(1)  # Componentler arası bekleme

        print("\n" + "="*80)
        print(f"[SUMMARY] {success_count}/{len(components)} component baslatildi")
        print("="*80 + "\n")

        if success_count == 0:
            print("[ERROR] Hicbir component baslatilamadi!")
            return False

        return True

    def monitor_processes(self):
        """Process'leri monitör et"""
        print("[MONITOR] Sistem calistirildi. Durum raporu:\n")

        try:
            while True:
                # Her 30 saniyede durum kontrolü
                time.sleep(30)

                running = 0
                dead = 0

                for proc_info in self.processes:
                    if proc_info['process'].poll() is None:
                        running += 1
                    else:
                        dead += 1

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Durum: {running} calisiyor, {dead} durdu")

                # Eğer tüm process'ler durduysa çık
                if dead == len(self.processes) and len(self.processes) > 0:
                    print("\n[WARNING] Tum componentler durdu. Cikis yapiliyor...")
                    break

        except KeyboardInterrupt:
            print("\n\n[STOP] Ctrl+C algilandi. Tum componentler durduruluyor...")
            self.stop_all()

    def stop_all(self):
        """Tüm componentleri durdur"""
        print("\n" + "="*80)
        print(" SISTEM KAPATILIYOR")
        print("="*80)

        for proc_info in self.processes:
            try:
                if proc_info['process'].poll() is None:
                    print(f"[STOP] {proc_info['name']} durduruluyor...")

                    if IS_WINDOWS:
                        # Windows: taskkill ile process tree'yi sonlandır
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc_info['process'].pid)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        # Linux/Mac: SIGTERM gönder
                        proc_info['process'].terminate()
                        time.sleep(2)

                        # Hala çalışıyorsa SIGKILL
                        if proc_info['process'].poll() is None:
                            proc_info['process'].kill()

                    print(f"[OK] {proc_info['name']} durduruldu")

            except Exception as e:
                print(f"[ERROR] {proc_info['name']} durdurma hatasi: {e}")

        print("="*80)
        print("[EXIT] Tum componentler kapatildi. Gorusmek uzere!")
        print("="*80 + "\n")

def main():
    """Ana fonksiyon"""
    master = ClaudeCodeCoinMaster()

    # Tüm componentleri başlat
    if master.start_all():
        # Process'leri monitör et
        master.monitor_processes()
    else:
        print("[ERROR] Sistem baslatilamadi!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[EXIT] Program sonlandirildi.")
        sys.exit(0)
