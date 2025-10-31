"""
Database Migration Script
Adds 'exchange' column to existing klines table
"""

import sqlite3
import os
from pathlib import Path

def migrate_database(db_path="data_output/binance_data.db"):
    """Add exchange column to existing database"""

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    print(f"🔧 Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if exchange column already exists
        cursor.execute("PRAGMA table_info(klines)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'exchange' in columns:
            print("✅ Column 'exchange' already exists!")
            conn.close()
            return True

        print("📝 Adding 'exchange' column...")

        # Add exchange column with default value 'binance'
        cursor.execute("""
            ALTER TABLE klines
            ADD COLUMN exchange TEXT DEFAULT 'binance'
        """)

        # Update existing records to have exchange = 'binance'
        cursor.execute("""
            UPDATE klines
            SET exchange = 'binance'
            WHERE exchange IS NULL
        """)

        conn.commit()

        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM klines WHERE exchange = 'binance'")
        count = cursor.fetchone()[0]

        print(f"✅ Migration successful!")
        print(f"   - Column 'exchange' added")
        print(f"   - {count} existing records updated to 'binance'")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🔧 ClaudeCodeCoin - Database Migration")
    print("=" * 70)
    print()

    # Determine database path
    script_dir = Path(__file__).parent.parent.parent
    db_path = script_dir / "data_output" / "binance_data.db"

    success = migrate_database(str(db_path))

    print()
    if success:
        print("✅ Migration complete! You can now run Gate.io collector.")
    else:
        print("❌ Migration failed. Please check the error messages above.")
    print("=" * 70)
