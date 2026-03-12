CREATE TABLE IF NOT EXISTS prices (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(16) NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    ts_unix BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prices_ticker_ts ON prices (ticker, ts_unix DESC);
