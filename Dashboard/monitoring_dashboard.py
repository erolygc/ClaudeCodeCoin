"""
ClaudeCodeCoin - Real-Time Monitoring Dashboard
Web tabanlı gerçek zamanlı sistem izleme paneli
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import time
import psutil

# Proje kök dizinini ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="ClaudeCodeCoin Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .error-text {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Database path
DB_PATH = project_root / "data_output" / "binance_data.db"

def get_db_connection():
    """Database bağlantısı"""
    if not DB_PATH.exists():
        return None
    return sqlite3.connect(str(DB_PATH))

def get_data_stats():
    """Veri istatistikleri"""
    conn = get_db_connection()
    if not conn:
        return None

    query = """
    SELECT
        symbol,
        exchange,
        COUNT(*) as bar_count,
        MIN(datetime) as first_bar,
        MAX(datetime) as last_bar,
        MAX(collected_at) as last_update
    FROM klines
    GROUP BY symbol, exchange
    ORDER BY exchange, symbol
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_recent_data(symbol="BTC_USDT", exchange="gate.io", limit=100):
    """Son N bar'ı getir"""
    conn = get_db_connection()
    if not conn:
        return None

    query = f"""
    SELECT *
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

def calculate_indicators(df):
    """Teknik indikatörleri hesapla"""
    if df is None or len(df) < 14:
        return df

    # RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # SMA (20, 50)
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()

    # EMA (12, 26)
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

    return df

def check_collectors_running():
    """Collector'ların çalışıp çalışmadığını kontrol et"""
    collectors = {
        'binance': False,
        'gateio': False
    }

    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            # Multi-coin veya standalone collector'ları kontrol et
            if 'multi_coin_binance_collector.py' in cmdline or 'standalone_binance_collector.py' in cmdline:
                collectors['binance'] = True
            if 'multi_coin_gateio_collector.py' in cmdline or 'standalone_gateio_collector.py' in cmdline:
                collectors['gateio'] = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return collectors

def get_system_stats():
    """Sistem istatistikleri"""
    stats = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }

    if DB_PATH.exists():
        stats['db_size_mb'] = DB_PATH.stat().st_size / (1024 * 1024)
    else:
        stats['db_size_mb'] = 0

    return stats

# Main Dashboard
def main():
    st.markdown('<h1 class="main-header">📊 ClaudeCodeCoin - Live Monitoring Dashboard</h1>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("⚙️ Ayarlar")

    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("Otomatik Yenileme", value=True)
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Yenileme Süresi (saniye)", 5, 60, 10)
        st.sidebar.info(f"Her {refresh_interval} saniyede bir yenilenecek")

    # Symbol selection
    st.sidebar.subheader("📈 Sembol Seçimi")
    selected_symbol = st.sidebar.selectbox("Sembol", ["BTC_USDT", "BTCUSDT", "ETH_USDT", "ETHUSDT"])
    selected_exchange = st.sidebar.selectbox("Exchange", ["gate.io", "binance"])

    # Data range
    data_limit = st.sidebar.slider("Gösterilecek Bar Sayısı", 50, 500, 100)

    # Main content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Genel Bakış", "📈 Grafikler", "🎯 Stratejiler", "🔥 Pump Signals", "🔧 Sistem"])

    # TAB 1: Overview
    with tab1:
        st.header("Veri Toplama Durumu")

        # Collector status
        collectors = check_collectors_running()
        col1, col2 = st.columns(2)

        with col1:
            status = "✅ ÇALIŞIYOR" if collectors['binance'] else "❌ DURDURULDU"
            color = "success-text" if collectors['binance'] else "error-text"
            st.markdown(f"**Binance Collector:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)

        with col2:
            status = "✅ ÇALIŞIYOR" if collectors['gateio'] else "❌ DURDURULDU"
            color = "success-text" if collectors['gateio'] else "error-text"
            st.markdown(f"**Gate.io Collector:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)

        st.divider()

        # Data statistics
        stats_df = get_data_stats()

        if stats_df is not None and not stats_df.empty:
            st.subheader("📊 Toplanan Veri İstatistikleri")

            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            total_bars = stats_df['bar_count'].sum()
            total_symbols = len(stats_df)

            with col1:
                st.metric("Toplam Bar", f"{total_bars:,}")

            with col2:
                st.metric("Toplam Sembol", total_symbols)

            with col3:
                if total_bars > 0:
                    oldest_bar = pd.to_datetime(stats_df['first_bar'].min())
                    st.metric("İlk Veri", oldest_bar.strftime("%H:%M"))

            with col4:
                if total_bars > 0:
                    newest_bar = pd.to_datetime(stats_df['last_bar'].max())
                    st.metric("Son Veri", newest_bar.strftime("%H:%M"))

            # Detailed table
            st.subheader("Detaylı İstatistikler")

            display_df = stats_df.copy()
            display_df['first_bar'] = pd.to_datetime(display_df['first_bar'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M')
            display_df['last_bar'] = pd.to_datetime(display_df['last_bar'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M')
            display_df['last_update'] = pd.to_datetime(display_df['last_update'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')

            # Status column
            def get_status(count):
                if count >= 100:
                    return "🟢 Mükemmel"
                elif count >= 50:
                    return "🟡 İyi"
                else:
                    return "🔴 Yetersiz"

            display_df['Durum'] = display_df['bar_count'].apply(get_status)

            st.dataframe(
                display_df.rename(columns={
                    'symbol': 'Sembol',
                    'exchange': 'Exchange',
                    'bar_count': 'Bar Sayısı',
                    'first_bar': 'İlk Bar',
                    'last_bar': 'Son Bar',
                    'last_update': 'Son Güncelleme'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("⚠️ Henüz veri toplanmamış! Collector'ları başlatın.")
            st.code(".\COLLECT_DATA_QUICK.bat")

    # TAB 2: Charts
    with tab2:
        st.header(f"📈 {selected_symbol} - {selected_exchange}")

        df = get_recent_data(selected_symbol, selected_exchange, data_limit)

        if df is not None and len(df) > 0:
            df = calculate_indicators(df)

            # Price chart with indicators
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.25, 0.25],
                subplot_titles=('Fiyat ve İndikatörler', 'RSI', 'MACD')
            )

            # Candlestick
            fig.add_trace(
                go.Candlestick(
                    x=df['datetime'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Fiyat'
                ),
                row=1, col=1
            )

            # Bollinger Bands
            if 'bb_upper' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['datetime'], y=df['bb_upper'], name='BB Üst',
                              line=dict(color='rgba(250,0,0,0.3)', width=1)),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['datetime'], y=df['bb_middle'], name='BB Orta',
                              line=dict(color='rgba(0,0,250,0.3)', width=1)),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['datetime'], y=df['bb_lower'], name='BB Alt',
                              line=dict(color='rgba(250,0,0,0.3)', width=1)),
                    row=1, col=1
                )

            # RSI
            if 'rsi' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['datetime'], y=df['rsi'], name='RSI',
                              line=dict(color='purple', width=2)),
                    row=2, col=1
                )
                # RSI levels
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)

            # MACD
            if 'macd' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['datetime'], y=df['macd'], name='MACD',
                              line=dict(color='blue', width=2)),
                    row=3, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['datetime'], y=df['macd_signal'], name='Signal',
                              line=dict(color='orange', width=2)),
                    row=3, col=1
                )
                fig.add_trace(
                    go.Bar(x=df['datetime'], y=df['macd_hist'], name='Histogram',
                          marker_color='gray'),
                    row=3, col=1
                )

            fig.update_layout(
                height=900,
                showlegend=True,
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # Latest values
            st.subheader("Son Değerler")
            col1, col2, col3, col4, col5 = st.columns(5)

            latest = df.iloc[-1]

            with col1:
                st.metric("Fiyat", f"${latest['close']:.2f}")

            with col2:
                if 'rsi' in latest:
                    rsi_val = latest['rsi']
                    if pd.notna(rsi_val):
                        st.metric("RSI", f"{rsi_val:.2f}")

            with col3:
                if 'macd' in latest:
                    macd_val = latest['macd']
                    if pd.notna(macd_val):
                        st.metric("MACD", f"{macd_val:.4f}")

            with col4:
                volume = latest['volume']
                st.metric("Volume", f"{volume:.2f}")

            with col5:
                st.metric("Bar Sayısı", len(df))
        else:
            st.warning(f"⚠️ {selected_symbol} için {selected_exchange}'de veri bulunamadı!")

    # TAB 3: Strategies
    with tab3:
        st.header("🎯 Strateji Sinyalleri")

        df = get_recent_data(selected_symbol, selected_exchange, 100)

        if df is not None and len(df) >= 50:
            df = calculate_indicators(df)
            latest = df.iloc[-1]

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("RSI Stratejisi")
                if 'rsi' in latest and pd.notna(latest['rsi']):
                    rsi = latest['rsi']

                    if rsi < 30:
                        st.success(f"🟢 AL SİNYALİ - RSI: {rsi:.2f} (Aşırı Satım)")
                    elif rsi > 70:
                        st.error(f"🔴 SAT SİNYALİ - RSI: {rsi:.2f} (Aşırı Alım)")
                    else:
                        st.info(f"⚪ NÖTR - RSI: {rsi:.2f}")
                else:
                    st.warning("Yetersiz veri")

            with col2:
                st.subheader("MACD Stratejisi")
                if 'macd' in latest and pd.notna(latest['macd']):
                    macd = latest['macd']
                    signal = latest['macd_signal']

                    if macd > signal:
                        st.success(f"🟢 YÜKSELIŞ TRENDİ")
                    else:
                        st.error(f"🔴 DÜŞÜŞ TRENDİ")

                    st.metric("MACD", f"{macd:.4f}")
                    st.metric("Signal", f"{signal:.4f}")
                else:
                    st.warning("Yetersiz veri")

            st.divider()

            # Bollinger Bands strategy
            st.subheader("Bollinger Bands Stratejisi")
            if all(k in latest for k in ['close', 'bb_upper', 'bb_lower', 'bb_middle']):
                if pd.notna(latest['bb_lower']):
                    price = latest['close']
                    bb_upper = latest['bb_upper']
                    bb_lower = latest['bb_lower']
                    bb_middle = latest['bb_middle']

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Fiyat", f"${price:.2f}")
                    with col2:
                        st.metric("BB Üst", f"${bb_upper:.2f}")
                    with col3:
                        st.metric("BB Alt", f"${bb_lower:.2f}")

                    if price <= bb_lower:
                        st.success("🟢 AL SİNYALİ - Fiyat alt banda değdi (Mean Reversion)")
                    elif price >= bb_upper:
                        st.error("🔴 SAT SİNYALİ - Fiyat üst banda değdi (Mean Reversion)")
                    else:
                        st.info("⚪ NÖTR - Fiyat bantlar içinde")
                else:
                    st.warning("Yetersiz veri")
        else:
            st.warning("⚠️ Strateji sinyalleri için en az 50 bar gerekli!")
            if df is not None:
                st.info(f"Mevcut: {len(df)} bar")

    # TAB 4: System
    with tab4:
        st.header("🔧 Sistem Durumu")

        sys_stats = get_system_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            cpu = sys_stats['cpu_percent']
            st.metric("CPU Kullanımı", f"{cpu:.1f}%")

        with col2:
            mem = sys_stats['memory_percent']
            st.metric("RAM Kullanımı", f"{mem:.1f}%")

        with col3:
            disk = sys_stats['disk_percent']
            st.metric("Disk Kullanımı", f"{disk:.1f}%")

        with col4:
            db_size = sys_stats['db_size_mb']
            st.metric("Veritabanı", f"{db_size:.2f} MB")

        st.divider()

        # Database info
        st.subheader("📁 Veritabanı Bilgileri")
        if DB_PATH.exists():
            st.success(f"✅ Veritabanı bulundu: {DB_PATH}")

            conn = get_db_connection()
            if conn:
                # Table info
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                st.write("**Tablolar:**")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    st.write(f"- `{table[0]}`: {count:,} kayıt")

                conn.close()
        else:
            st.error(f"❌ Veritabanı bulunamadı: {DB_PATH}")

        st.divider()

        # Logs
        st.subheader("📋 Son Loglar")
        log_dir = project_root / "logs"

        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            if log_files:
                selected_log = st.selectbox("Log Dosyası", [f.name for f in log_files])

                if selected_log:
                    log_path = log_dir / selected_log
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            last_lines = lines[-50:]  # Son 50 satır
                            st.code(''.join(last_lines))
                    except Exception as e:
                        st.error(f"Log okunamadı: {e}")
            else:
                st.info("Henüz log dosyası yok")
        else:
            st.info("Log klasörü bulunamadı")

    # TAB 5: Pump Signals
    with tab5:
        st.header("🔥 Pump & Dump Detection")

        # Import pump detection engine
        try:
            sys.path.insert(0, str(project_root / "Phase6_PumpDetection"))
            from pump_detection_engine import PumpDetectionEngine, PumpLevel

            # Create engine
            engine = PumpDetectionEngine(db_path=str(DB_PATH))

            # Sidebar controls
            st.sidebar.subheader("🔥 Pump Detector Ayarları")
            scan_exchange = st.sidebar.selectbox("Tarama Exchange", ["gate.io", "binance"], key="pump_exchange")
            min_confidence = st.sidebar.slider("Minimum Confidence", 30, 90, 50)

            # Analyze selected symbol
            st.subheader(f"📊 {selected_symbol} Analizi")

            with st.spinner("Pump sinyalleri aranıyor..."):
                signals = engine.analyze_symbol(selected_symbol, selected_exchange)

            if signals:
                # Filter by confidence
                filtered_signals = [s for s in signals if s.confidence >= min_confidence]

                if filtered_signals:
                    st.success(f"✅ {len(filtered_signals)} pump sinyali tespit edildi!")

                    # Display each signal
                    for i, signal in enumerate(filtered_signals, 1):
                        # Color based on level
                        if signal.level.value == "critical":
                            color = "🔴"
                            border_color = "#dc3545"
                        elif signal.level.value == "high":
                            color = "🟠"
                            border_color = "#fd7e14"
                        elif signal.level.value == "medium":
                            color = "🟡"
                            border_color = "#ffc107"
                        else:
                            color = "🟢"
                            border_color = "#28a745"

                        with st.container():
                            st.markdown(f"""
                            <div style="border-left: 4px solid {border_color}; padding-left: 1rem; margin: 1rem 0;">
                                <h4>{color} Sinyal #{i} - {signal.level.value.upper()}</h4>
                            </div>
                            """, unsafe_allow_html=True)

                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("Confidence", f"{signal.confidence:.1f}%")
                            with col2:
                                st.metric("Fiyat Değişimi", f"{signal.price_change_pct:+.2f}%")
                            with col3:
                                st.metric("Hacim Değişimi", f"{signal.volume_change_pct:+.1f}%")
                            with col4:
                                st.metric("Zaman", f"{signal.time_window_minutes}m")

                            st.info(f"💬 {signal.message}")

                            # Indicators
                            with st.expander("📊 Detaylı İndikatörler"):
                                st.json(signal.indicators)

                            st.divider()
                else:
                    st.info(f"ℹ️ {min_confidence}% confidence üzerinde sinyal bulunamadı.")
            else:
                st.info("✅ Normal piyasa koşulları - Pump sinyali yok.")

            st.divider()

            # Scan all symbols
            st.subheader("🔍 Tüm Semboller Taraması")

            if st.button("Tüm Coinleri Tara", type="primary"):
                with st.spinner("Tüm semboller taranıyor... (Bu biraz zaman alabilir)"):
                    all_results = engine.scan_all_symbols(exchange=scan_exchange)

                if all_results:
                    st.success(f"✅ {len(all_results)} sembolde pump sinyali bulundu!")

                    # Create summary table
                    summary_data = []
                    for symbol, symbol_signals in all_results.items():
                        for signal in symbol_signals:
                            if signal.confidence >= min_confidence:
                                summary_data.append({
                                    'Sembol': symbol,
                                    'Seviye': signal.level.value.upper(),
                                    'Confidence': f"{signal.confidence:.1f}%",
                                    'Fiyat Değişimi': f"{signal.price_change_pct:+.2f}%",
                                    'Hacim Değişimi': f"{signal.volume_change_pct:+.1f}%",
                                    'Mesaj': signal.message[:60] + "..."
                                })

                    if summary_data:
                        summary_df = pd.DataFrame(summary_data)

                        # Sort by confidence
                        summary_df['Confidence_num'] = summary_df['Confidence'].str.rstrip('%').astype(float)
                        summary_df = summary_df.sort_values('Confidence_num', ascending=False)
                        summary_df = summary_df.drop('Confidence_num', axis=1)

                        st.dataframe(summary_df, use_container_width=True, hide_index=True)

                        # Top pump coins
                        st.subheader("🏆 En Yüksek Confidence")
                        top_3 = summary_df.head(3)

                        cols = st.columns(3)
                        for idx, (i, row) in enumerate(top_3.iterrows()):
                            with cols[idx]:
                                st.metric(
                                    label=f"#{idx+1} {row['Sembol']}",
                                    value=row['Confidence'],
                                    delta=row['Fiyat Değişimi']
                                )
                    else:
                        st.info(f"ℹ️ {min_confidence}% confidence üzerinde sinyal bulunamadı.")
                else:
                    st.info("✅ Hiçbir sembolde pump sinyali tespit edilmedi.")

            # Alert history (if exists)
            st.divider()
            st.subheader("📜 Alert Geçmişi")

            alert_dir = project_root / "pump_alerts"
            if alert_dir.exists():
                alert_files = list(alert_dir.glob("pump_alerts_*.json"))
                if alert_files:
                    latest_alert_file = max(alert_files, key=lambda p: p.stat().st_mtime)

                    with open(latest_alert_file, 'r', encoding='utf-8') as f:
                        import json
                        alerts = json.load(f)

                    if alerts:
                        st.info(f"📁 {len(alerts)} alert kaydı bulundu")

                        # Recent alerts (last 10)
                        recent_alerts = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)[:10]

                        alert_data = []
                        for alert in recent_alerts:
                            alert_data.append({
                                'Zaman': alert['timestamp'].split('T')[1][:8],
                                'Sembol': alert['symbol'],
                                'Seviye': alert['level'].upper(),
                                'Confidence': f"{alert['confidence']:.1f}%",
                                'Fiyat Δ': f"{alert['price_change_pct']:+.2f}%"
                            })

                        alert_df = pd.DataFrame(alert_data)
                        st.dataframe(alert_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Henüz alert kaydı yok")
            else:
                st.info("Alert klasörü bulunamadı")

            # Help section
            with st.expander("ℹ️ Pump Detection Nasıl Çalışır?"):
                st.markdown("""
                ### 🎯 Tespit Edilen Sinyaller

                1. **Volume Spike (Hacim Patlaması)**
                   - Normal hacmin 3-10x üzeri
                   - Aniden artan alım/satım aktivitesi

                2. **Price Surge (Hızlı Fiyat Artışı)**
                   - 5-15 dakikada %10+ artış
                   - Momentum göstergeleri

                3. **Volatility Spike (Volatilite Patlaması)**
                   - ATR'nin 2.5x+ artması
                   - Fiyat dalgalanmalarının artması

                4. **Coordinated Buying (Koordineli Alım)**
                   - Ardışık yeşil (yükseliş) barları
                   - Hacimle birlikte sürekli alım

                ### 📊 Confidence Seviyeleri

                - **🔴 CRITICAL (85%+)**: Çok yüksek pump olasılığı
                - **🟠 HIGH (70-85%)**: Yüksek pump olasılığı
                - **🟡 MEDIUM (50-70%)**: Orta pump olasılığı
                - **🟢 LOW (30-50%)**: Düşük pump olasılığı

                ### ⚠️ Önemli Notlar

                - Pump detection bir **tahmin** sistemidir, %100 doğruluk garantisi yoktur
                - High confidence bile kesin alım sinyali değildir
                - Her zaman risk yönetimi kurallarını uygulayın
                - Dump (düşüş) fazı çok hızlı gerçekleşebilir
                - Sadece eğitim ve araştırma amaçlıdır
                """)

        except ImportError as e:
            st.error("❌ Pump Detection Engine yüklenemedi!")
            st.info("Phase6_PumpDetection modülünün kurulu olduğundan emin olun.")
            st.code(str(e))
        except Exception as e:
            st.error(f"❌ Hata oluştu: {e}")

    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
