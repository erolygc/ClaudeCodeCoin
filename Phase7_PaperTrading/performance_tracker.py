"""
Performance Tracker
Trading performans analizi ve raporlama
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import config


class PerformanceTracker:
    """Trading performans metrikleri"""

    def __init__(self, db_path: str = config.TRADES_DB):
        self.db_path = Path(db_path)

    def get_all_trades(self) -> pd.DataFrame:
        """Tüm tamamlanmış işlemleri getir"""
        conn = sqlite3.connect(str(self.db_path))

        df = pd.read_sql_query("""
            SELECT * FROM positions
            WHERE status = 'CLOSED'
            ORDER BY exit_time DESC
        """, conn)

        conn.close()

        if not df.empty:
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df['exit_time'] = pd.to_datetime(df['exit_time'])
            df['duration_minutes'] = (df['exit_time'] - df['entry_time']).dt.total_seconds() / 60
            df['pnl_percent'] = (df['pnl'] / (df['entry_price'] * df['quantity'])) * 100

        return df

    def get_balance_history(self) -> pd.DataFrame:
        """Bakiye geçmişini getir"""
        conn = sqlite3.connect(str(self.db_path))

        df = pd.read_sql_query("""
            SELECT timestamp, balance, total_pnl
            FROM balance_history
            ORDER BY timestamp ASC
        """, conn)

        conn.close()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    def calculate_metrics(self) -> Dict:
        """Detaylı performans metriklerini hesapla"""
        df = self.get_all_trades()

        if df.empty:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_pnl': 0,
                'total_pnl': 0,
                'max_win': 0,
                'max_loss': 0,
                'avg_duration': 0,
                'best_symbol': None,
                'worst_symbol': None
            }

        # Temel metrikler
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] <= 0]

        metrics = {
            'total_trades': len(df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(df) * 100) if len(df) > 0 else 0,

            # P&L metrikleri
            'total_pnl': df['pnl'].sum(),
            'avg_pnl': df['pnl'].mean(),
            'avg_pnl_percent': df['pnl_percent'].mean(),
            'max_win': df['pnl'].max(),
            'max_loss': df['pnl'].min(),

            # Kazanan/Kaybeden ortalamaları
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,

            # Süre metrikleri
            'avg_duration': df['duration_minutes'].mean(),
            'max_duration': df['duration_minutes'].max(),
            'min_duration': df['duration_minutes'].min(),

            # Exit sebepleri
            'exit_reasons': df['close_reason'].value_counts().to_dict(),

            # Sembol bazlı
            'trades_by_symbol': df['symbol'].value_counts().to_dict(),
            'pnl_by_symbol': df.groupby('symbol')['pnl'].sum().to_dict(),
        }

        # En iyi ve en kötü semboller
        if len(df) > 0:
            pnl_by_symbol = df.groupby('symbol')['pnl'].sum().sort_values(ascending=False)
            metrics['best_symbol'] = pnl_by_symbol.index[0] if len(pnl_by_symbol) > 0 else None
            metrics['worst_symbol'] = pnl_by_symbol.index[-1] if len(pnl_by_symbol) > 0 else None

        # Confidence bazlı performans
        confidence_bins = [0, 50, 70, 85, 100]
        confidence_labels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        df['confidence_level'] = pd.cut(df['confidence'], bins=confidence_bins, labels=confidence_labels)

        metrics['performance_by_confidence'] = df.groupby('confidence_level').agg({
            'pnl': ['sum', 'mean', 'count']
        }).to_dict()

        return metrics

    def print_report(self):
        """Detaylı performans raporu yazdır"""
        metrics = self.calculate_metrics()

        print("\n" + "="*70)
        print("📊 PERFORMANS RAPORU")
        print("="*70)

        print(f"\n💼 GENEL ÖZET:")
        print(f"   Toplam İşlem: {metrics['total_trades']}")
        print(f"   Kazanan: {metrics['winning_trades']} | Kaybeden: {metrics['losing_trades']}")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")

        print(f"\n💰 P&L ANALİZİ:")
        print(f"   Toplam P&L: ${metrics['total_pnl']:.2f}")
        print(f"   Ortalama P&L: ${metrics['avg_pnl']:.2f} ({metrics['avg_pnl_percent']:+.2f}%)")
        print(f"   En Büyük Kazanç: ${metrics['max_win']:.2f}")
        print(f"   En Büyük Kayıp: ${metrics['max_loss']:.2f}")
        print(f"   Ortalama Kazanç: ${metrics['avg_win']:.2f}")
        print(f"   Ortalama Kayıp: ${metrics['avg_loss']:.2f}")

        print(f"\n⏱️  SÜRE ANALİZİ:")
        print(f"   Ortalama Pozisyon Süresi: {metrics['avg_duration']:.1f} dakika")
        print(f"   En Uzun: {metrics['max_duration']:.1f} dakika")
        print(f"   En Kısa: {metrics['min_duration']:.1f} dakika")

        if metrics.get('exit_reasons'):
            print(f"\n🚪 ÇIKIŞ SEBEPLERİ:")
            for reason, count in metrics['exit_reasons'].items():
                print(f"   {reason}: {count} işlem")

        if metrics.get('best_symbol'):
            print(f"\n🏆 EN İYİ/KÖTÜ SEMBOLLER:")
            print(f"   En İyi: {metrics['best_symbol']} (${metrics['pnl_by_symbol'][metrics['best_symbol']]:.2f})")
            print(f"   En Kötü: {metrics['worst_symbol']} (${metrics['pnl_by_symbol'][metrics['worst_symbol']]:.2f})")

        print("\n" + "="*70 + "\n")

    def export_to_csv(self, output_path: str = "paper_trading_results.csv"):
        """Sonuçları CSV'ye aktar"""
        df = self.get_all_trades()

        if df.empty:
            print("⚠️  Henüz tamamlanmış işlem yok")
            return

        df.to_csv(output_path, index=False)
        print(f"✅ Sonuçlar {output_path} dosyasına aktarıldı")


if __name__ == "__main__":
    tracker = PerformanceTracker()
    tracker.print_report()
