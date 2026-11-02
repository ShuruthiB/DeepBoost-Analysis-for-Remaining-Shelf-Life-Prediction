-- SpoilSense AI SQLite schema
-- The backend applies this structure automatically on first startup.

PRAGMA journal_mode = DELETE;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    id TEXT PRIMARY KEY,
    batch TEXT NOT NULL,
    supplier TEXT NOT NULL,
    variety TEXT NOT NULL,
    shelf TEXT NOT NULL,
    ph REAL NOT NULL CHECK (ph BETWEEN 0 AND 14),
    moisture REAL NOT NULL CHECK (moisture BETWEEN 0 AND 1.5),
    temp REAL NOT NULL CHECK (temp BETWEEN -50 AND 80),
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending', 'SAFE', 'WARNING', 'CRITICAL')),
    days REAL
);

CREATE TABLE IF NOT EXISTS inventory_decay (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    days_remaining REAL NOT NULL CHECK (days_remaining >= 0),
    status TEXT NOT NULL
        CHECK (status IN ('Pending', 'SAFE', 'WARNING', 'CRITICAL')),
    UNIQUE (inventory_id, recorded_at),
    FOREIGN KEY (inventory_id) REFERENCES inventory(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_inventory_variety
    ON inventory(variety);

CREATE INDEX IF NOT EXISTS idx_inventory_status
    ON inventory(status);

CREATE INDEX IF NOT EXISTS idx_inventory_decay_recorded_at
    ON inventory_decay(recorded_at);

CREATE INDEX IF NOT EXISTS idx_inventory_decay_inventory_id
    ON inventory_decay(inventory_id);
