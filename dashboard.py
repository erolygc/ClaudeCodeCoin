"""
ClaudeCodeCoin - Professional Trading Dashboard
Gate.io Futures Style Dashboard with Real-time Data

Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
import json
from pathlib import Path
import time

# Page config
st.set_page_config(
    page_title="ClaudeCodeCoin Trading Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main {
        background-color: #0a0e27;
    }
    .stMetric {
        background-color: #1a1f3a;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2a3f5f;
    }
    .metric-positive {
        color: #00ff88 !important;
    }
    .metric-negative {
        color: #ff4444 !important;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f3a;
        border-radius: 8px 8px 0 0;
        color: #ffffff;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2a3f5f;
    }
</style>
""", unsafe_allow_html=True)

# Database paths
DB_PATH = Path("data_output/binance_data.db")
PAPER_TRADES_DB = Path("Phase7_PaperTrading/paper_trades.db")
PUMP_ALERTS_DIR = Path("pump_alerts")

@st.cache_data(ttl=1)
def get_latest_prices(limit=20):
    """Get latest prices for top coins"""
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(str(DB_PATH))
    query = """
        SELECT symbol, close as price, volume, datetime,
               (close - open) / open * 100 as change_pct
        FROM klines
        WHERE exchange = 'gate.io'
        GROUP BY symbol
        HAVING datetime = MAX(datetime)
        ORDER BY volume DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

@st.cache_data(ttl=1)
def get_candlestick_data(symbol, limit=100):
    """Get candlestick data for chart"""
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(str(DB_PATH))
    query = """
        SELECT datetime, open, high, low, close, volume
        FROM klines
        WHERE symbol = ? AND exchange = 'gate.io'
        ORDER BY datetime DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(symbol, limit))
    conn.close()

    if not df.empty:
        df = df.iloc[::-1]  # Reverse to chronological order
        df['datetime'] = pd.to_datetime(df['datetime'])

    return df

@st.cache_data(ttl=1)
def get_open_positions():
    """Get open positions from paper trading"""
    if not PAPER_TRADES_DB.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(str(PAPER_TRADES_DB))
    query = """
        SELECT symbol, entry_price, current_price, quantity,
               unrealized_pnl, unrealized_pnl_pct, stop_loss, take_profit,
               entry_time, confidence
        FROM positions
        WHERE status = 'open'
        ORDER BY entry_time DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=1)
def get_trade_history(limit=50):
    """Get closed trades"""
    if not PAPER_TRADES_DB.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(str(PAPER_TRADES_DB))
    query = """
        SELECT symbol, entry_price, exit_price, quantity,
               realized_pnl, realized_pnl_pct, exit_reason,
               entry_time, exit_time, confidence
        FROM positions
        WHERE status = 'closed'
        ORDER BY exit_time DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

@st.cache_data(ttl=1)
def get_portfolio_stats():
    """Get portfolio statistics"""
    if not PAPER_TRADES_DB.exists():
        return {}

    conn = sqlite3.connect(str(PAPER_TRADES_DB))

    # Get balance
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM portfolio_state ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    balance = result[0] if result else 10000.0

    # Get total P&L
    cursor.execute("SELECT SUM(realized_pnl) FROM positions WHERE status = 'closed'")
    result = cursor.fetchone()
    total_pnl = result[0] if result and result[0] else 0.0

    # Get win rate
    cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'closed' AND realized_pnl > 0")
    wins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'closed'")
    total_trades = cursor.fetchone()[0]

    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    # Get open positions count
    cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'open'")
    open_positions = cursor.fetchone()[0]

    conn.close()

    return {
        "balance": balance,
        "total_pnl": total_pnl,
        "win_rate": win_rate,
        "total_trades": total_trades,
        "open_positions": open_positions
    }

@st.cache_data(ttl=5)
def get_recent_pump_alerts(limit=10):
    """Get recent pump alerts"""
    today = datetime.now().strftime("%Y%m%d")
    alert_file = PUMP_ALERTS_DIR / f"pump_alerts_{today}.json"

    if not alert_file.exists():
        return []

    try:
        with open(alert_file, 'r') as f:
            alerts = json.load(f)

        # Sort by timestamp (most recent first)
        alerts = sorted(alerts, key=lambda x: x.get('timestamp', ''), reverse=True)
        return alerts[:limit]
    except:
        return []

def create_candlestick_chart(df, symbol):
    """Create professional candlestick chart"""
    if df.empty:
        return go.Figure()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{symbol} Price', 'Volume')
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ),
        row=1, col=1
    )

    # Volume bars
    colors = ['#00ff88' if close >= open else '#ff4444'
              for close, open in zip(df['close'], df['open'])]

    fig.add_trace(
        go.Bar(
            x=df['datetime'],
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.5
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#0a0e27',
        plot_bgcolor='#1a1f3a',
        font=dict(color='#ffffff'),
        showlegend=False
    )

    fig.update_xaxes(gridcolor='#2a3f5f', showgrid=True)
    fig.update_yaxes(gridcolor='#2a3f5f', showgrid=True)

    return fig

def main():
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.title("🚀 ClaudeCodeCoin Trading Dashboard")

    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with col3:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)

    # Auto refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()

    # Portfolio Stats
    st.markdown("### 💰 Portfolio Overview")
    stats = get_portfolio_stats()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Balance",
            f"${stats.get('balance', 0):.2f}",
            delta=None
        )

    with col2:
        pnl = stats.get('total_pnl', 0)
        st.metric(
            "Total P&L",
            f"${pnl:.2f}",
            delta=f"{pnl/10000*100:.2f}%" if pnl != 0 else "0%",
            delta_color="normal"
        )

    with col3:
        win_rate = stats.get('win_rate', 0)
        st.metric(
            "Win Rate",
            f"{win_rate:.1f}%",
            delta=None
        )

    with col4:
        st.metric(
            "Total Trades",
            stats.get('total_trades', 0),
            delta=None
        )

    with col5:
        st.metric(
            "Open Positions",
            stats.get('open_positions', 0),
            delta=None
        )

    st.divider()

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Markets", "💼 Positions", "🚀 Pump Alerts", "📊 History"])

    with tab1:
        # Market overview
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Live Markets")
            prices_df = get_latest_prices(20)

            if not prices_df.empty:
                # Format the dataframe
                prices_df['price'] = prices_df['price'].apply(lambda x: f"${x:.6f}")
                prices_df['volume'] = prices_df['volume'].apply(lambda x: f"{x:,.0f}")
                prices_df['change_pct'] = prices_df['change_pct'].apply(lambda x: f"{x:+.2f}%")

                st.dataframe(
                    prices_df,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
            else:
                st.info("Waiting for market data...")

        with col2:
            st.markdown("### Select Coin")
            prices_df_raw = get_latest_prices(20)
            if not prices_df_raw.empty:
                selected_symbol = st.selectbox(
                    "Symbol",
                    prices_df_raw['symbol'].tolist(),
                    index=0
                )

                # Show chart
                if selected_symbol:
                    st.markdown(f"### {selected_symbol} Chart")
                    candle_df = get_candlestick_data(selected_symbol, 100)

                    if not candle_df.empty:
                        fig = create_candlestick_chart(candle_df, selected_symbol)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No data for {selected_symbol}")

    with tab2:
        st.markdown("### 💼 Open Positions")
        positions_df = get_open_positions()

        if not positions_df.empty:
            # Format columns
            for col in ['entry_price', 'current_price', 'stop_loss', 'take_profit']:
                if col in positions_df.columns:
                    positions_df[col] = positions_df[col].apply(lambda x: f"${x:.6f}" if pd.notna(x) else "-")

            positions_df['unrealized_pnl'] = positions_df['unrealized_pnl'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "$0.00")
            positions_df['unrealized_pnl_pct'] = positions_df['unrealized_pnl_pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "0%")
            positions_df['confidence'] = positions_df['confidence'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "0%")

            st.dataframe(
                positions_df,
                use_container_width=True,
                height=400,
                hide_index=True
            )
        else:
            st.info("No open positions")

    with tab3:
        st.markdown("### 🚀 Recent Pump Alerts")
        alerts = get_recent_pump_alerts(20)

        if alerts:
            for alert in alerts:
                level = alert.get('level', 'low')

                # Color based on level
                if level == 'critical':
                    color = "#ff4444"
                    icon = "🔥"
                elif level == 'high':
                    color = "#ff9944"
                    icon = "⚠️"
                elif level == 'medium':
                    color = "#ffff44"
                    icon = "📊"
                else:
                    color = "#4444ff"
                    icon = "ℹ️"

                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 2, 2, 2])

                    with col1:
                        st.markdown(f"### {icon}")

                    with col2:
                        st.markdown(f"**{alert.get('symbol', 'N/A')}**")
                        st.caption(alert.get('timestamp', 'N/A'))

                    with col3:
                        st.markdown(f"Price: **{alert.get('price_change_pct', 0):+.1f}%**")
                        st.caption(f"Volume: {alert.get('volume_change_pct', 0):.0f}%")

                    with col4:
                        st.markdown(f"Confidence: **{alert.get('confidence', 0):.0f}%**")
                        st.caption(f"Level: {level.upper()}")

                    st.divider()
        else:
            st.info("No recent pump alerts")

    with tab4:
        st.markdown("### 📊 Trade History")
        history_df = get_trade_history(50)

        if not history_df.empty:
            # Format columns
            for col in ['entry_price', 'exit_price']:
                if col in history_df.columns:
                    history_df[col] = history_df[col].apply(lambda x: f"${x:.6f}" if pd.notna(x) else "-")

            history_df['realized_pnl'] = history_df['realized_pnl'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "$0.00")
            history_df['realized_pnl_pct'] = history_df['realized_pnl_pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "0%")
            history_df['confidence'] = history_df['confidence'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "0%")

            st.dataframe(
                history_df,
                use_container_width=True,
                height=500,
                hide_index=True
            )
        else:
            st.info("No trade history")

    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("⚡ ClaudeCodeCoin v1.0")

    with col2:
        st.caption(f"🕐 Last updated: {datetime.now().strftime('%H:%M:%S')}")

    with col3:
        st.caption("💚 System: Online")

if __name__ == "__main__":
    main()
