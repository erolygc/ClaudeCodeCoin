"""
Windows Emoji Encoding Fix
Tüm log dosyalarındaki emojileri ASCII karakterlerle değiştirir
"""
import re
from pathlib import Path

# Emoji mapping
EMOJI_MAP = {
    '💰': '[MONEY]',
    '📊': '[CHART]',
    '🚀': '[ROCKET]',
    '🛡️': '[SHIELD]',
    '🎯': '[TARGET]',
    '💵': '[DOLLAR]',
    '📋': '[CLIPBOARD]',
    '⚠️': '[WARNING]',
    '📄': '[PAGE]',
    '⏰': '[CLOCK]',
    '✅': '[CHECK]',
    '⊘': '[X]',
    '📬': '[MAILBOX]',
    '📈': '[TRENDING_UP]',
    '📍': '[PIN]',
    '🔴': '[RED]',
    '🟡': '[YELLOW]',
    '🟢': '[GREEN]',
    '🔔': '[BELL]',
    '💾': '[DISK]',
    '🔥': '[FIRE]',
    '📌': '[PUSHPIN]',
    '⏭️': '[SKIP]',
}

def remove_emojis_from_file(file_path: Path):
    """Bir dosyadan emojileri kaldır"""
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Emojileri değiştir
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)

        # Değişiklik varsa kaydet
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

    return False

def main():
    print("="*80)
    print("WINDOWS EMOJI ENCODING FIX")
    print("="*80)
    print()

    # Python dosyalarını bul
    python_files = [
        'Phase7_PaperTrading/paper_trading_engine.py',
        'Phase7_PaperTrading/position_manager.py',
        'run_paper_trading_test.py',
        'run_pump_scan_once.py',
    ]

    base_path = Path(__file__).parent
    fixed_count = 0

    for file_path in python_files:
        full_path = base_path / file_path
        print(f"Processing: {file_path}...", end=" ")

        if remove_emojis_from_file(full_path):
            print("✓ Fixed")
            fixed_count += 1
        else:
            print("- No changes")

    print()
    print("="*80)
    print(f"Fixed {fixed_count} files")
    print("="*80)
    print()
    print("Now run: python run_paper_trading_test.py")

if __name__ == "__main__":
    main()
