"""
Professional Futures Trading Dashboard
Binance/Gate.io style dashboard for futures trading monitoring
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import time

# Page config
st.set_page_config(
    page_title="ClaudeCodeCoin Futures Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .profit {
        color: #00ff00;
    }
    .loss {
        color: #ff4444;
    }
    .warning {
        color: #ffaa00;
    }
    </style>
    """, unsafe_allow_html=True)

# Database paths
FUTURES_DB = "Phase8_FuturesTrading/data_output/futures_trading.db"
MARKET_DB = "data_output/binance_data.db"

# Check if databases exist
if not Path(FUTURES_DB).exists():
    st.error(f"❌ Futures database not found: {FUTURES_DB}")
    st.info("Run the futures trading engine first to create positions.")
    st.stop()


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data(ttl=5)
def load_account_summary():
    """Load account summary"""
    try:
        conn = sqlite3.connect(FUTURES_DB)

        # Get latest account state
        query = """
            SELECT balance, margin_used, unrealized_pnl, total_pnl,
                   open_positions, equity, timestamp
            FROM account_state
            ORDER BY timestamp DESC
            LIMIT 1
        """
        df = pd.read_sql_query(query, conn)

        if df.empty:
            conn.close()
            return None

        summary = df.iloc[0].to_dict()

        # Calculate additional metrics
        summary['free_margin'] = summary['balance'] - summary['margin_used']
        summary['margin_usage_percent'] = (summary['margin_used'] / summary['balance'] * 100) if summary['balance'] > 0 else 0

        # Get trade statistics
        stats_query = """
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN realized_pnl <= 0 THEN 1 ELSE 0 END) as losing_trades,
                AVG(CASE WHEN realized_pnl > 0 THEN realized_pnl ELSE 0 END) as avg_win,
                AVG(CASE WHEN realized_pnl < 0 THEN realized_pnl ELSE 0 END) as avg_loss,
                MAX(realized_pnl) as best_trade,
                MIN(realized_pnl) as worst_trade
            FROM futures_positions
            WHERE status = 'CLOSED'
        """
        stats_df = pd.read_sql_query(stats_query, conn)
        conn.close()

        if not stats_df.empty:
            stats = stats_df.iloc[0].to_dict()
            summary.update(stats)

            if stats['total_trades'] > 0:
                summary['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100
            else:
                summary['win_rate'] = 0

            # Calculate profit factor
            if stats['avg_loss'] < 0:
                summary['profit_factor'] = abs(stats['avg_win'] / stats['avg_loss'])
            else:
                summary['profit_factor'] = 0

        return summary

    except Exception as e:
        st.error(f"Error loading account summary: {e}")
        return None


@st.cache_data(ttl=5)
def load_open_positions():
    """Load open positions"""
    try:
        conn = sqlite3.connect(FUTURES_DB)

        query = """
            SELECT symbol, contract, entry_price, current_price,
                   position_size, quantity, leverage, margin_used,
                   unrealized_pnl, unrealized_pnl_percent,
                   liquidation_price, liquidation_distance_percent,
                   stop_loss, take_profit, entry_time, confidence, signal_type
            FROM futures_positions
            WHERE status = 'OPEN'
            ORDER BY entry_time DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df['duration'] = (datetime.now() - df['entry_time']).dt.total_seconds() / 60

        return df

    except Exception as e:
        st.error(f"Error loading open positions: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=10)
def load_closed_positions(limit=50):
    """Load closed positions"""
    try:
        conn = sqlite3.connect(FUTURES_DB)

        query = f"""
            SELECT symbol, entry_price, current_price as exit_price,
                   position_size, leverage, realized_pnl,
                   entry_time, exit_time, confidence, signal_type
            FROM futures_positions
            WHERE status = 'CLOSED'
            ORDER BY exit_time DESC
            LIMIT {limit}
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df['exit_time'] = pd.to_datetime(df['exit_time'])
            df['duration_minutes'] = (df['exit_time'] - df['entry_time']).dt.total_seconds() / 60
            df['roi_percent'] = (df['realized_pnl'] / (df['position_size'] / df['leverage'])) * 100

        return df

    except Exception as e:
        st.error(f"Error loading closed positions: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=10)
def load_pnl_history(days=7):
    """Load P&L history"""
    try:
        conn = sqlite3.connect(FUTURES_DB)

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        query = f"""
            SELECT timestamp, balance, equity, total_pnl, unrealized_pnl, margin_used
            FROM account_state
            WHERE timestamp >= '{cutoff_date}'
            ORDER BY timestamp ASC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    except Exception as e:
        st.error(f"Error loading P&L history: {e}")
        return pd.DataFrame()


# ============================================================================
# HEADER
# ============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.title("📈 Futures Trading Dashboard")
    st.markdown("**ClaudeCodeCoin** - Professional Futures Trading Monitor")

with col2:
    mode = "PAPER TRADING 📄"
    st.markdown(f"### {mode}")
    st.markdown(f"*Last update: {datetime.now().strftime('%H:%M:%S')}*")

# Auto-refresh
if st.sidebar.checkbox("Auto-refresh (5s)", value=True):
    time.sleep(5)
    st.rerun()

# ============================================================================
# ACCOUNT OVERVIEW
# ============================================================================

st.markdown("---")
st.markdown("## 💼 Account Overview")

summary = load_account_summary()

if summary:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        balance_change = summary['total_pnl']
        delta_color = "normal" if balance_change >= 0 else "inverse"
        st.metric(
            "Balance",
            f"${summary['balance']:.2f}",
            f"${balance_change:.2f}",
            delta_color=delta_color
        )

    with col2:
        equity_change = summary['unrealized_pnl']
        delta_color = "normal" if equity_change >= 0 else "inverse"
        st.metric(
            "Total Equity",
            f"${summary['equity']:.2f}",
            f"${equity_change:.2f}",
            delta_color=delta_color
        )

    with col3:
        margin_pct = summary['margin_usage_percent']
        margin_color = "🟢" if margin_pct < 50 else "🟡" if margin_pct < 75 else "🔴"
        st.metric(
            "Margin Used",
            f"${summary['margin_used']:.2f}",
            f"{margin_pct:.1f}% {margin_color}"
        )

    with col4:
        st.metric(
            "Free Margin",
            f"${summary['free_margin']:.2f}",
            ""
        )

    with col5:
        unrealized_pnl = summary['unrealized_pnl']
        delta_color = "normal" if unrealized_pnl >= 0 else "inverse"
        st.metric(
            "Unrealized P&L",
            f"${unrealized_pnl:.2f}",
            "",
            delta_color=delta_color
        )

    # Performance metrics
    st.markdown("### 📊 Performance Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        total_trades = summary.get('total_trades', 0)
        st.metric("Total Trades", f"{total_trades}")

    with col2:
        win_rate = summary.get('win_rate', 0)
        wr_color = "🟢" if win_rate >= 60 else "🟡" if win_rate >= 40 else "🔴"
        st.metric("Win Rate", f"{win_rate:.1f}% {wr_color}")

    with col3:
        winning = summary.get('winning_trades', 0)
        st.metric("Winners", f"{winning}", delta_color="normal")

    with col4:
        losing = summary.get('losing_trades', 0)
        st.metric("Losers", f"{losing}", delta_color="inverse")

    with col5:
        avg_win = summary.get('avg_win', 0)
        st.metric("Avg Win", f"${avg_win:.2f}", delta_color="normal")

    with col6:
        avg_loss = summary.get('avg_loss', 0)
        st.metric("Avg Loss", f"${avg_loss:.2f}", delta_color="inverse")

else:
    st.warning("No account data available. Start trading engine first.")

# ============================================================================
# OPEN POSITIONS
# ============================================================================

st.markdown("---")
st.markdown("## 📊 Open Positions")

open_positions = load_open_positions()

if not open_positions.empty:
    st.markdown(f"**{len(open_positions)} positions currently open**")

    # Format dataframe for display
    display_df = open_positions.copy()

    # Add colored P&L
    def color_pnl(val):
        color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
        return f'color: {color}'

    # Add colored liquidation distance
    def color_liq(val):
        if val > 25:
            return 'color: green'
        elif val > 15:
            return 'color: orange'
        else:
            return 'color: red'

    # Format columns
    display_df['Entry Price'] = display_df['entry_price'].apply(lambda x: f"${x:.6f}")
    display_df['Current Price'] = display_df['current_price'].apply(lambda x: f"${x:.6f}")
    display_df['Position Size'] = display_df['position_size'].apply(lambda x: f"${x:.2f}")
    display_df['Margin'] = display_df['margin_used'].apply(lambda x: f"${x:.2f}")
    display_df['Unrealized P&L'] = display_df['unrealized_pnl'].apply(lambda x: f"${x:.2f}")
    display_df['ROE %'] = display_df['unrealized_pnl_percent'].apply(lambda x: f"{x:.2f}%")
    display_df['Liquidation Price'] = display_df['liquidation_price'].apply(lambda x: f"${x:.6f}")
    display_df['Liq Distance'] = display_df['liquidation_distance_percent'].apply(lambda x: f"{x:.1f}%")
    display_df['Stop Loss'] = display_df['stop_loss'].apply(lambda x: f"${x:.6f}")
    display_df['Take Profit'] = display_df['take_profit'].apply(lambda x: f"${x:.6f}")
    display_df['Duration (min)'] = display_df['duration'].apply(lambda x: f"{x:.0f}")
    display_df['Confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1f}%")

    # Select columns to display
    columns_to_show = [
        'symbol', 'Entry Price', 'Current Price', 'Position Size',
        'leverage', 'Margin', 'Unrealized P&L', 'ROE %',
        'Liquidation Price', 'Liq Distance',
        'Stop Loss', 'Take Profit', 'Duration (min)', 'Confidence', 'signal_type'
    ]

    st.dataframe(
        display_df[columns_to_show].rename(columns={
            'symbol': 'Symbol',
            'leverage': 'Leverage',
            'signal_type': 'Signal'
        }),
        use_container_width=True,
        height=400
    )

    # Liquidation risk analysis
    st.markdown("### ⚠️ Liquidation Risk Analysis")

    col1, col2, col3 = st.columns(3)

    safe_positions = len(open_positions[open_positions['liquidation_distance_percent'] > 25])
    warning_positions = len(open_positions[
        (open_positions['liquidation_distance_percent'] >= 15) &
        (open_positions['liquidation_distance_percent'] <= 25)
    ])
    danger_positions = len(open_positions[open_positions['liquidation_distance_percent'] < 15])

    with col1:
        st.metric("🟢 Safe (>25%)", safe_positions)

    with col2:
        st.metric("🟡 Warning (15-25%)", warning_positions)

    with col3:
        st.metric("🔴 Danger (<15%)", danger_positions)

    # Show positions close to liquidation
    if danger_positions > 0:
        st.error("⚠️ WARNING: Positions close to liquidation!")
        danger_df = open_positions[open_positions['liquidation_distance_percent'] < 15]
        for _, pos in danger_df.iterrows():
            st.warning(f"{pos['symbol']}: Only {pos['liquidation_distance_percent']:.1f}% from liquidation!")

else:
    st.info("No open positions. Waiting for pump signals...")

# ============================================================================
# CLOSED POSITIONS HISTORY
# ============================================================================

st.markdown("---")
st.markdown("## 📜 Closed Positions History")

closed_positions = load_closed_positions(limit=50)

if not closed_positions.empty:
    st.markdown(f"**Last {len(closed_positions)} closed positions**")

    # Format dataframe
    display_df = closed_positions.copy()
    display_df['Entry Price'] = display_df['entry_price'].apply(lambda x: f"${x:.6f}")
    display_df['Exit Price'] = display_df['exit_price'].apply(lambda x: f"${x:.6f}")
    display_df['Position Size'] = display_df['position_size'].apply(lambda x: f"${x:.2f}")
    display_df['Realized P&L'] = display_df['realized_pnl'].apply(lambda x: f"${x:.2f}")
    display_df['ROI %'] = display_df['roi_percent'].apply(lambda x: f"{x:.2f}%")
    display_df['Duration (min)'] = display_df['duration_minutes'].apply(lambda x: f"{x:.0f}")
    display_df['Entry Time'] = display_df['entry_time'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['Exit Time'] = display_df['exit_time'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['Confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1f}%")

    columns_to_show = [
        'symbol', 'Entry Time', 'Exit Time', 'Entry Price', 'Exit Price',
        'Position Size', 'leverage', 'Realized P&L', 'ROI %',
        'Duration (min)', 'Confidence', 'signal_type'
    ]

    st.dataframe(
        display_df[columns_to_show].rename(columns={
            'symbol': 'Symbol',
            'leverage': 'Leverage',
            'signal_type': 'Signal'
        }),
        use_container_width=True,
        height=400
    )

    # Performance breakdown
    st.markdown("### 📊 Performance Breakdown")

    col1, col2, col3 = st.columns(3)

    winners = closed_positions[closed_positions['realized_pnl'] > 0]
    losers = closed_positions[closed_positions['realized_pnl'] < 0]

    with col1:
        st.markdown("**Winners**")
        if not winners.empty:
            st.metric("Count", len(winners))
            st.metric("Total P&L", f"${winners['realized_pnl'].sum():.2f}")
            st.metric("Avg P&L", f"${winners['realized_pnl'].mean():.2f}")
            st.metric("Best Trade", f"${winners['realized_pnl'].max():.2f}")

    with col2:
        st.markdown("**Losers**")
        if not losers.empty:
            st.metric("Count", len(losers))
            st.metric("Total P&L", f"${losers['realized_pnl'].sum():.2f}")
            st.metric("Avg P&L", f"${losers['realized_pnl'].mean():.2f}")
            st.metric("Worst Trade", f"${losers['realized_pnl'].min():.2f}")

    with col3:
        st.markdown("**Overall**")
        st.metric("Total Trades", len(closed_positions))
        win_rate = (len(winners) / len(closed_positions)) * 100 if len(closed_positions) > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
        st.metric("Total P&L", f"${closed_positions['realized_pnl'].sum():.2f}")

        if len(winners) > 0 and len(losers) > 0:
            profit_factor = abs(winners['realized_pnl'].sum() / losers['realized_pnl'].sum())
            st.metric("Profit Factor", f"{profit_factor:.2f}")

else:
    st.info("No closed positions yet.")

# ============================================================================
# P&L CHART
# ============================================================================

st.markdown("---")
st.markdown("## 📈 P&L Chart")

pnl_history = load_pnl_history(days=7)

if not pnl_history.empty:
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Equity & Balance', 'P&L'),
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1
    )

    # Equity & Balance
    fig.add_trace(
        go.Scatter(
            x=pnl_history['timestamp'],
            y=pnl_history['equity'],
            name='Total Equity',
            line=dict(color='#00ff00', width=2)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=pnl_history['timestamp'],
            y=pnl_history['balance'],
            name='Balance',
            line=dict(color='#0099ff', width=2)
        ),
        row=1, col=1
    )

    # P&L
    fig.add_trace(
        go.Scatter(
            x=pnl_history['timestamp'],
            y=pnl_history['total_pnl'],
            name='Total P&L',
            fill='tozeroy',
            line=dict(color='#ff9900', width=2)
        ),
        row=2, col=1
    )

    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="USD", row=1, col=1)
    fig.update_yaxes(title_text="P&L (USD)", row=2, col=1)

    fig.update_layout(
        height=600,
        showlegend=True,
        hovermode='x unified',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Not enough data for P&L chart.")

# ============================================================================
# SIDEBAR: CONTROLS & STATS
# ============================================================================

st.sidebar.markdown("## 🎛️ Controls")

if st.sidebar.button("🔄 Force Refresh"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("📥 Export Data"):
    st.sidebar.info("Export feature coming soon!")

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ Settings")

show_closed_limit = st.sidebar.slider("Closed positions limit", 10, 100, 50)

st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 Quick Stats")

if summary:
    st.sidebar.metric("Open Positions", f"{summary.get('open_positions', 0)}/10")
    st.sidebar.metric("Margin Usage", f"{summary.get('margin_usage_percent', 0):.1f}%")
    st.sidebar.metric("Win Rate", f"{summary.get('win_rate', 0):.1f}%")

    # Risk indicator
    margin_pct = summary.get('margin_usage_percent', 0)
    if margin_pct > 75:
        st.sidebar.error("⚠️ High margin usage!")
    elif margin_pct > 50:
        st.sidebar.warning("🟡 Moderate margin usage")
    else:
        st.sidebar.success("🟢 Low margin usage")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Documentation")
st.sidebar.markdown("[Implementation Guide](Phase8_FuturesTrading/IMPLEMENTATION_GUIDE.md)")
st.sidebar.markdown("[Configuration](Phase8_FuturesTrading/config_futures.py)")

st.sidebar.markdown("---")
st.sidebar.markdown("*ClaudeCodeCoin v2.0*")
st.sidebar.markdown("*Futures Trading Dashboard*")
