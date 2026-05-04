-- ============================================
-- Memory App - 数据库表结构 (PostgreSQL)
-- 使用方式: psql -d memory_app -f init_db.sql
-- ============================================

CREATE TABLE IF NOT EXISTS cards (
    id              SERIAL PRIMARY KEY,
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    ease_factor     DOUBLE PRECISION NOT NULL DEFAULT 2.5,
    interval_days   INTEGER NOT NULL DEFAULT 0,
    next_review_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tags (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100) NOT NULL UNIQUE,
    color   VARCHAR(7) NOT NULL DEFAULT '#6366f1'
);

CREATE TABLE IF NOT EXISTS card_tags (
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (card_id, tag_id)
);

CREATE TABLE IF NOT EXISTS review_logs (
    id          SERIAL PRIMARY KEY,
    card_id     INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    rating      VARCHAR(20) NOT NULL,
    reviewed_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_cards_next_review ON cards(next_review_at);
CREATE INDEX IF NOT EXISTS idx_review_logs_card ON review_logs(card_id);
