"""
ClaudeCodeCoin - Professional Trade Dashboard
Binance/Gate.io tarzı profesyonel trading dashboard

Özellikler:
- Gerçek zamanlı fiyat grafikleri (Candlestick)
- Açık pozisyonlar tablosu
- P&L grafikleri
- Portfolio özeti
- Son pump alertleri
- Trading geçmişi
- Sistem durumu
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json

# Sayfa yapılandırması
st.set_page_config(
    page_title="ClaudeCodeCoin - Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #0e1117;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #262730;
    }
    .profit {
        color: #00ff00;
    }
    .loss {
        color: #ff0000;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)

# Database paths
DB_PATH = "data_output/binance_data.db"
TRADES_DB = "data_output/paper_trading.db"
ALERTS_DIR = Path("pump_alerts")


class TradeDashboard:
    """Ana dashboard sınıfı"""

    def __init__(self):
        self.db_path = DB_PATH
        self.trades_db = TRADES_DB

    def get_portfolio_summary(self):
        """Portfolio özetini al"""
        try:
            conn = sqlite3.connect(self.trades_db)

            # Son bakiye
            balance_query = """
                SELECT balance, total_pnl
                FROM balance_history
                ORDER BY timestamp DESC LIMIT 1
            """
            balance_df = pd.read_sql_query(balance_query, conn)

            # Açık pozisyonlar
            open_pos_query = """
                SELECT COUNT(*) as count, SUM(entry_price * quantity) as value
                FROM positions
                WHERE status='OPEN'
            """
            open_pos_df = pd.read_sql_query(open_pos_query, conn)

            # Trade istatistikleri
            stats_query = """
                SELECT
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning,
                    SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losing,
                    AVG(pnl) as avg_pnl,
                    SUM(pnl) as total_pnl
                FROM positions
                WHERE status='CLOSED'
            """
            stats_df = pd.read_sql_query(stats_query, conn)

            conn.close()

            return {
                'balance': balance_df['balance'].iloc[0] if not balance_df.empty else 10000,
                'total_pnl': balance_df['total_pnl'].iloc[0] if not balance_df.empty else 0,
                'open_positions': int(open_pos_df['count'].iloc[0]) if not open_pos_df.empty else 0,
                'open_value': float(open_pos_df['value'].iloc[0]) if not open_pos_df.empty and open_pos_df['value'].iloc[0] else 0,
                'total_trades': int(stats_df['total_trades'].iloc[0]) if not stats_df.empty and stats_df['total_trades'].iloc[0] else 0,
                'winning': int(stats_df['winning'].iloc[0]) if not stats_df.empty and stats_df['winning'].iloc[0] else 0,
                'losing': int(stats_df['losing'].iloc[0]) if not stats_df.empty and stats_df['losing'].iloc[0] else 0,
                'avg_pnl': float(stats_df['avg_pnl'].iloc[0]) if not stats_df.empty and stats_df['avg_pnl'].iloc[0] else 0,
            }
        except Exception as e:
            st.error(f"Portfolio özeti alınamadı: {e}")
            return {
                'balance': 10000, 'total_pnl': 0, 'open_positions': 0,
                'open_value': 0, 'total_trades': 0, 'winning': 0, 'losing': 0, 'avg_pnl': 0
            }

    def get_open_positions(self):
        """Açık pozisyonları al"""
        try:
            conn = sqlite3.connect(self.trades_db)
            query = """
                SELECT symbol, entry_price, quantity, confidence,
                       stop_loss, take_profit, entry_time
                FROM positions
                WHERE status='OPEN'
                ORDER BY entry_time DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

    def get_recent_alerts(self, limit=10):
        """Son pump alert'lerini al"""
        try:
            today = datetime.now().strftime("%Y%m%d")
            alert_file = ALERTS_DIR / f"pump_alerts_{today}.json"

            if not alert_file.exists():
                return pd.DataFrame()

            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                alerts = data if isinstance(data, list) else data.get('alerts', [])

            # DataFrame'e çevir
            if alerts:
                df = pd.DataFrame(alerts)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp', ascending=False).head(limit)
                return df

            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    def get_candlestick_data(self, symbol, exchange="gate.io", limit=100):
        """Candlestick verisini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT timestamp, datetime, open, high, low, close, volume
                FROM klines
                WHERE symbol = ? AND exchange = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(symbol, exchange, limit))
            conn.close()

            if not df.empty:
                df = df.sort_values('timestamp')
                df['datetime'] = pd.to_datetime(df['datetime'])
                return df

            return pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    def plot_candlestick(self, symbol, exchange="gate.io"):
        """Candlestick grafiği oluştur"""
        df = self.get_candlestick_data(symbol, exchange)

        if df.empty:
            st.warning(f"{symbol} için veri bulunamadı")
            return None

        # Candlestick + Volume grafiği
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.05,
            subplot_titles=(f'{symbol} - Fiyat', 'Hacim')
        )

        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=df['datetime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Fiyat',
                increasing_line_color='#00ff00',
                decreasing_line_color='#ff0000'
            ),
            row=1, col=1
        )

        # Volume
        colors = ['#00ff00' if close >= open else '#ff0000'
                 for close, open in zip(df['close'], df['open'])]

        fig.add_trace(
            go.Bar(
                x=df['datetime'],
                y=df['volume'],
                name='Hacim',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )

        # Layout
        fig.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            showlegend=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#262730')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#262730')

        return fig

    def plot_pnl_chart(self):
        """P&L zaman serisi grafiği"""
        try:
            conn = sqlite3.connect(self.trades_db)
            query = """
                SELECT timestamp, balance, total_pnl
                FROM balance_history
                ORDER BY timestamp ASC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return None

            df['timestamp'] = pd.to_datetime(df['timestamp'])

            fig = go.Figure()

            # Balance line
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['balance'],
                name='Bakiye',
                line=dict(color='#00bfff', width=2)
            ))

            # Starting line
            fig.add_hline(y=10000, line_dash="dash", line_color="gray",
                         annotation_text="Başlangıç")

            fig.update_layout(
                height=400,
                template='plotly_dark',
                xaxis_title="Zaman",
                yaxis_title="Bakiye ($)",
                showlegend=True,
                margin=dict(l=50, r=50, t=50, b=50)
            )

            return fig
        except Exception as e:
            return None


def main():
    """Ana dashboard fonksiyonu"""

    # Title
    st.title("📈 ClaudeCodeCoin - Professional Trading Dashboard")
    st.markdown("---")

    # Dashboard instance
    dashboard = TradeDashboard()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Ayarlar")

        # Refresh button
        if st.button("🔄 Yenile", use_container_width=True):
            st.rerun()

        st.markdown("---")

        # Exchange seçimi
        exchange = st.selectbox("Exchange", ["gate.io", "binance"])

        # Symbol seçimi
        symbol_input = st.text_input("Symbol", "BTC_USDT")

        st.markdown("---")
        st.markdown("### 📊 Sistem Durumu")

        # Database stats
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM klines")
            total_candles = cursor.fetchone()[0]
            conn.close()
            st.metric("Toplam Candlestick", f"{total_candles:,}")
        except:
            st.metric("Toplam Candlestick", "N/A")

    # Main content
    # Portfolio özeti
    summary = dashboard.get_portfolio_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 Bakiye",
            f"${summary['balance']:,.2f}",
            delta=f"{summary['total_pnl']:+,.2f}"
        )

    with col2:
        win_rate = (summary['winning'] / summary['total_trades'] * 100) if summary['total_trades'] > 0 else 0
        st.metric(
            "🎯 Win Rate",
            f"{win_rate:.1f}%",
            delta=f"{summary['winning']}/{summary['total_trades']}"
        )

    with col3:
        st.metric(
            "📊 Açık Pozisyon",
            summary['open_positions'],
            delta=f"${summary['open_value']:,.2f}"
        )

    with col4:
        st.metric(
            "💵 Ort. P&L",
            f"${summary['avg_pnl']:,.2f}",
            delta=f"{summary['total_trades']} trades"
        )

    st.markdown("---")

    # Ana içerik - 2 kolon
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Chart", "💼 Positions", "🚨 Alerts", "📊 Analytics"])

    with tab1:
        st.subheader(f"📈 {symbol_input} - Live Chart")
        fig = dashboard.plot_candlestick(symbol_input, exchange)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("💼 Açık Pozisyonlar")
        positions_df = dashboard.get_open_positions()

        if not positions_df.empty:
            # Hesaplamalar
            positions_df['value'] = positions_df['entry_price'] * positions_df['quantity']
            positions_df['sl_distance'] = ((positions_df['stop_loss'] / positions_df['entry_price']) - 1) * 100
            positions_df['tp_distance'] = ((positions_df['take_profit'] / positions_df['entry_price']) - 1) * 100

            # Tablo
            st.dataframe(
                positions_df[[
                    'symbol', 'entry_price', 'quantity', 'value',
                    'confidence', 'sl_distance', 'tp_distance', 'entry_time'
                ]].style.format({
                    'entry_price': '${:.4f}',
                    'quantity': '{:.2f}',
                    'value': '${:.2f}',
                    'confidence': '{:.1f}%',
                    'sl_distance': '{:+.2f}%',
                    'tp_distance': '{:+.2f}%'
                }),
                use_container_width=True,
                height=400
            )
        else:
            st.info("Henüz açık pozisyon yok")

    with tab3:
        st.subheader("🚨 Son Pump Alertleri")
        alerts_df = dashboard.get_recent_alerts(20)

        if not alerts_df.empty:
            # Tablo
            display_df = alerts_df[['timestamp', 'symbol', 'confidence', 'price_change_pct', 'volume_change_pct']].copy()
            display_df.columns = ['Zaman', 'Symbol', 'Confidence', 'Fiyat Değişimi', 'Hacim Değişimi']

            st.dataframe(
                display_df.style.format({
                    'Confidence': '{:.1f}%',
                    'Fiyat Değişimi': '{:+.2f}%',
                    'Hacim Değişimi': '{:+.2f}%'
                }),
                use_container_width=True,
                height=500
            )
        else:
            st.info("Bugün henüz alert yok")

    with tab4:
        st.subheader("📊 Portfolio Analytics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💹 P&L Grafiği")
            pnl_fig = dashboard.plot_pnl_chart()
            if pnl_fig:
                st.plotly_chart(pnl_fig, use_container_width=True)
            else:
                st.info("Henüz trading geçmişi yok")

        with col2:
            st.markdown("#### 📈 Trade İstatistikleri")
            if summary['total_trades'] > 0:
                st.metric("Toplam Trade", summary['total_trades'])
                st.metric("Kazanan", summary['winning'], delta=f"{win_rate:.1f}%")
                st.metric("Kaybeden", summary['losing'])
                st.metric("Ortalama P&L", f"${summary['avg_pnl']:.2f}")
            else:
                st.info("Henüz kapalı trade yok")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "ClaudeCodeCoin v1.0 | Auto-refresh: 30s | "
        f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    # Auto-refresh her 30 saniyede
    import time

    main()

    # Auto-refresh
    time.sleep(30)
    st.rerun()
