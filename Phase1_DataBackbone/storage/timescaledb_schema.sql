-- ============================================================================
-- ClaudeCodeCoin - TimescaleDB Schema
-- Time-series database schema for storing market data, indicators, and signals
-- ============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- RAW MARKET DATA TABLES
-- ============================================================================

-- OHLCV Candlestick Data
CREATE TABLE IF NOT EXISTS raw_klines (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    close_volume DOUBLE PRECISION,
    number_of_trades INTEGER,
    taker_buy_base_volume DOUBLE PRECISION,
    taker_buy_quote_volume DOUBLE PRECISION,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, exchange, symbol, interval)
);

-- Convert to hypertable (TimescaleDB feature)
SELECT create_hypertable('raw_klines', 'time', if_not_exists => TRUE);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_raw_klines_symbol_time
    ON raw_klines (symbol, time DESC);
CREATE INDEX IF NOT EXISTS idx_raw_klines_exchange_symbol
    ON raw_klines (exchange, symbol, time DESC);

-- Order Book Snapshots (Level 2)
CREATE TABLE IF NOT EXISTS raw_orderbook (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('bid', 'ask')),
    price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    depth_level INTEGER NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('raw_orderbook', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_raw_orderbook_symbol_time
    ON raw_orderbook (symbol, time DESC);

-- Individual Trades (Level 3)
CREATE TABLE IF NOT EXISTS raw_trades (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    trade_id VARCHAR(50),
    side VARCHAR(4) CHECK (side IN ('buy', 'sell')),
    price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    is_buyer_maker BOOLEAN,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('raw_trades', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_raw_trades_symbol_time
    ON raw_trades (symbol, time DESC);

-- ============================================================================
-- DERIVATIVES DATA
-- ============================================================================

-- Futures Funding Rates
CREATE TABLE IF NOT EXISTS funding_rates (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    funding_rate DOUBLE PRECISION NOT NULL,
    funding_interval_hours INTEGER,
    next_funding_time TIMESTAMPTZ,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, exchange, symbol)
);

SELECT create_hypertable('funding_rates', 'time', if_not_exists => TRUE);

-- Open Interest
CREATE TABLE IF NOT EXISTS open_interest (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open_interest DOUBLE PRECISION NOT NULL,
    open_interest_value DOUBLE PRECISION,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, exchange, symbol)
);

SELECT create_hypertable('open_interest', 'time', if_not_exists => TRUE);

-- Liquidations
CREATE TABLE IF NOT EXISTS liquidations (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(5) CHECK (side IN ('long', 'short')),
    quantity DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('liquidations', 'time', if_not_exists => TRUE);

-- ============================================================================
-- ON-CHAIN DATA
-- ============================================================================

-- Whale Wallet Activity
CREATE TABLE IF NOT EXISTS whale_activity (
    time TIMESTAMPTZ NOT NULL,
    blockchain VARCHAR(50) NOT NULL,
    token VARCHAR(20) NOT NULL,
    wallet_address VARCHAR(100) NOT NULL,
    transaction_type VARCHAR(20),
    amount DOUBLE PRECISION NOT NULL,
    value_usd DOUBLE PRECISION,
    destination VARCHAR(100),
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('whale_activity', 'time', if_not_exists => TRUE);

-- On-Chain Metrics (from Glassnode, CryptoQuant, etc.)
CREATE TABLE IF NOT EXISTS onchain_metrics (
    time TIMESTAMPTZ NOT NULL,
    token VARCHAR(20) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    source VARCHAR(50),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, token, metric_name)
);

SELECT create_hypertable('onchain_metrics', 'time', if_not_exists => TRUE);

-- ============================================================================
-- SOCIAL MEDIA & SENTIMENT DATA
-- ============================================================================

-- Social Media Mentions and Sentiment
CREATE TABLE IF NOT EXISTS social_sentiment (
    time TIMESTAMPTZ NOT NULL,
    platform VARCHAR(50) NOT NULL,
    token VARCHAR(20) NOT NULL,
    mentions_count INTEGER,
    sentiment_score DOUBLE PRECISION,
    sentiment_label VARCHAR(20),
    engagement_count INTEGER,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('social_sentiment', 'time', if_not_exists => TRUE);

-- ============================================================================
-- TECHNICAL INDICATORS (CALCULATED FEATURES)
-- ============================================================================

-- Technical Indicators Table
CREATE TABLE IF NOT EXISTS indicators (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    indicator_value DOUBLE PRECISION NOT NULL,
    parameters JSONB,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, exchange, symbol, interval, indicator_name)
);

SELECT create_hypertable('indicators', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_indicators_symbol_name
    ON indicators (symbol, indicator_name, time DESC);

-- ============================================================================
-- SIGNALS TABLE (FROM PHASE 2)
-- ============================================================================

-- Trading Signals
CREATE TABLE IF NOT EXISTS signals (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('BUY', 'SELL', 'NEUTRAL')),
    strategy_name VARCHAR(100) NOT NULL,
    confidence_score DOUBLE PRECISION,
    target_price DOUBLE PRECISION,
    stop_loss DOUBLE PRECISION,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('signals', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_signals_symbol_time
    ON signals (symbol, time DESC);
CREATE INDEX IF NOT EXISTS idx_signals_strategy
    ON signals (strategy_name, time DESC);

-- ============================================================================
-- TRADES & POSITIONS (FROM PHASE 4)
-- ============================================================================

-- Order Management
CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('buy', 'sell')),
    order_type VARCHAR(20) NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION,
    status VARCHAR(20) NOT NULL,
    filled_quantity DOUBLE PRECISION DEFAULT 0,
    average_fill_price DOUBLE PRECISION,
    commission DOUBLE PRECISION,
    strategy_name VARCHAR(100),
    signal_id UUID,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_symbol_status
    ON orders (symbol, status, created_at DESC);

-- Positions
CREATE TABLE IF NOT EXISTS positions (
    position_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opened_at TIMESTAMPTZ NOT NULL,
    closed_at TIMESTAMPTZ,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(5) NOT NULL CHECK (side IN ('long', 'short')),
    entry_price DOUBLE PRECISION NOT NULL,
    exit_price DOUBLE PRECISION,
    quantity DOUBLE PRECISION NOT NULL,
    pnl DOUBLE PRECISION,
    pnl_percentage DOUBLE PRECISION,
    commission_paid DOUBLE PRECISION,
    strategy_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'open',
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_positions_symbol_status
    ON positions (symbol, status, opened_at DESC);

-- ============================================================================
-- CONTINUOUS AGGREGATES (Pre-computed views for performance)
-- ============================================================================

-- 5-minute OHLCV aggregation from 1-minute data
CREATE MATERIALIZED VIEW IF NOT EXISTS klines_5m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS time,
    exchange,
    symbol,
    '5m' AS interval,
    FIRST(open, time) AS open,
    MAX(high) AS high,
    MIN(low) AS low,
    LAST(close, time) AS close,
    SUM(volume) AS volume,
    SUM(number_of_trades) AS number_of_trades
FROM raw_klines
WHERE interval = '1m'
GROUP BY time_bucket('5 minutes', time), exchange, symbol
WITH NO DATA;

-- 15-minute aggregation
CREATE MATERIALIZED VIEW IF NOT EXISTS klines_15m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('15 minutes', time) AS time,
    exchange,
    symbol,
    '15m' AS interval,
    FIRST(open, time) AS open,
    MAX(high) AS high,
    MIN(low) AS low,
    LAST(close, time) AS close,
    SUM(volume) AS volume,
    SUM(number_of_trades) AS number_of_trades
FROM raw_klines
WHERE interval = '1m'
GROUP BY time_bucket('15 minutes', time), exchange, symbol
WITH NO DATA;

-- 1-hour aggregation
CREATE MATERIALIZED VIEW IF NOT EXISTS klines_1h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS time,
    exchange,
    symbol,
    '1h' AS interval,
    FIRST(open, time) AS open,
    MAX(high) AS high,
    MIN(low) AS low,
    LAST(close, time) AS close,
    SUM(volume) AS volume,
    SUM(number_of_trades) AS number_of_trades
FROM raw_klines
WHERE interval = '1m'
GROUP BY time_bucket('1 hour', time), exchange, symbol
WITH NO DATA;

-- Refresh policies (automatic updates every 1 minute)
SELECT add_continuous_aggregate_policy('klines_5m',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE);

SELECT add_continuous_aggregate_policy('klines_15m',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE);

SELECT add_continuous_aggregate_policy('klines_1h',
    start_offset => INTERVAL '6 hours',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE);

-- ============================================================================
-- DATA RETENTION POLICIES
-- ============================================================================

-- Keep raw 1-minute data for 90 days
SELECT add_retention_policy('raw_klines', INTERVAL '90 days', if_not_exists => TRUE);

-- Keep order book data for 30 days (high volume)
SELECT add_retention_policy('raw_orderbook', INTERVAL '30 days', if_not_exists => TRUE);

-- Keep trades for 60 days
SELECT add_retention_policy('raw_trades', INTERVAL '60 days', if_not_exists => TRUE);

-- Keep indicators for 180 days (6 months)
SELECT add_retention_policy('indicators', INTERVAL '180 days', if_not_exists => TRUE);

-- ============================================================================
-- COMPRESSION POLICIES (Save storage space)
-- ============================================================================

ALTER TABLE raw_klines SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'exchange, symbol, interval'
);

SELECT add_compression_policy('raw_klines', INTERVAL '7 days', if_not_exists => TRUE);

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to get latest price for a symbol
CREATE OR REPLACE FUNCTION get_latest_price(
    p_exchange VARCHAR,
    p_symbol VARCHAR,
    p_interval VARCHAR DEFAULT '1m'
)
RETURNS TABLE (
    time TIMESTAMPTZ,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT k.time, k.open, k.high, k.low, k.close, k.volume
    FROM raw_klines k
    WHERE k.exchange = p_exchange
      AND k.symbol = p_symbol
      AND k.interval = p_interval
    ORDER BY k.time DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate percentage change
CREATE OR REPLACE FUNCTION calculate_percentage_change(
    current_price DOUBLE PRECISION,
    previous_price DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION AS $$
BEGIN
    IF previous_price = 0 THEN
        RETURN NULL;
    END IF;
    RETURN ((current_price - previous_price) / previous_price) * 100;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANT PERMISSIONS (Adjust as needed)
-- ============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ccc_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ccc_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ccc_user;

-- ============================================================================
-- COMPLETED
-- ============================================================================

SELECT 'ClaudeCodeCoin TimescaleDB schema created successfully!' AS status;
