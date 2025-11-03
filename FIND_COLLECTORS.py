"""
FIND COLLECTORS - Binance collector dosyasının yerini bul
"""

import os
from pathlib import Path

print("=" * 80)
print("COLLECTOR DOSYALARINI ARIYORUM...")
print("=" * 80)
print()

# Tüm olası konumları ara
possible_paths = [
    "Phase1_DataBackbone/data_collectors/binance_collector_multi_coin.py",
    "data_collectors/binance_collector_multi_coin.py",
    "collectors/binance_collector_multi_coin.py",
    "Phase1_DataBackbone/binance_collector_multi_coin.py",
]

found = False

for path_str in possible_paths:
    path = Path(path_str)
    if path.exists():
        print(f"✅ BULUNDU: {path}")
        print()
        print("ÇALIŞTIRMAK İÇİN:")
        print(f"   cd {path.parent}")
        print(f"   python {path.name}")
        print()
        found = True
        break

if not found:
    print("❌ Binance collector bulunamadı!")
    print()
    print("Tüm .py dosyalarını arıyorum...")
    print()

    # Recursive search
    for root, dirs, files in os.walk('.'):
        # Skip venv and .git
        dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', 'node_modules']]

        for file in files:
            if 'binance' in file.lower() and 'collector' in file.lower() and file.endswith('.py'):
                full_path = Path(root) / file
                print(f"   {full_path}")

print("=" * 80)
