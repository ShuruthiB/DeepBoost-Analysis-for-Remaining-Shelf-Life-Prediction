from __future__ import annotations

from typing import Final, Literal

TARGET_COLUMN: Final[str] = "Target_Shelf_Life_Days"
STATIC_COLUMNS: Final[tuple[str, str]] = ("pH", "Moisture")
TEMPERATURE_COLUMNS: Final[tuple[str, ...]] = tuple(
    f"Temp_Day{i}" for i in range(1, 6)
)
REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    *STATIC_COLUMNS,
    *TEMPERATURE_COLUMNS,
    "Variety",
    TARGET_COLUMN,
)
INVENTORY_STATUSES: Final[tuple[str, ...]] = (
    "Pending",
    "SAFE",
    "WARNING",
    "CRITICAL",
)
InventoryStatus = Literal["Pending", "SAFE", "WARNING", "CRITICAL"]

DEMO_INVENTORY_ROWS: Final[tuple[tuple[object, ...], ...]] = (
    ("INV-DEMO-001", "BN-DEMO-001", "AgriCorp", "Banana", "A", 4.8, 0.75, 14.0, "SAFE", 16.1),
    ("INV-DEMO-002", "OR-DEMO-001", "SunFarms", "Orange", "B", 3.8, 0.87, 5.0, "SAFE", 28.7),
    ("INV-DEMO-003", "PN-DEMO-001", "TropiGrow", "Pineapple", "C", 3.6, 0.86, 18.0, "WARNING", 8.2),
    ("INV-DEMO-004", "TM-DEMO-001", "RedVine", "Tomato", "D", 4.3, 0.94, 15.0, "SAFE", 21.8),
    ("INV-DEMO-005", "BN-DEMO-002", "AgriCorp", "Banana", "A", 4.7, 0.76, 18.0, "SAFE", 15.3),
    ("INV-DEMO-006", "BN-DEMO-003", "FreshLink", "Banana", "E", 4.5, 0.81, 21.0, "SAFE", 15.0),
    ("INV-DEMO-007", "BN-DEMO-004", "GreenBasket", "Banana", "A", 5.0, 0.74, 12.0, "SAFE", 16.8),
    ("INV-DEMO-008", "OR-DEMO-002", "SunFarms", "Orange", "B", 3.9, 0.88, 7.0, "SAFE", 29.8),
    ("INV-DEMO-009", "OR-DEMO-003", "CitrusCo", "Orange", "F", 3.6, 0.85, 10.0, "SAFE", 26.4),
    ("INV-DEMO-010", "OR-DEMO-004", "SunFarms", "Orange", "B", 4.1, 0.89, 4.0, "SAFE", 31.8),
    ("INV-DEMO-011", "PN-DEMO-002", "TropiGrow", "Pineapple", "C", 3.7, 0.84, 14.0, "WARNING", 8.9),
    ("INV-DEMO-012", "PN-DEMO-003", "IslandHarvest", "Pineapple", "H", 3.5, 0.87, 20.0, "WARNING", 7.8),
    ("INV-DEMO-013", "PN-DEMO-004", "IslandHarvest", "Pineapple", "H", 3.9, 0.82, 11.0, "WARNING", 9.5),
    ("INV-DEMO-014", "TM-DEMO-002", "RedVine", "Tomato", "D", 4.5, 0.92, 18.0, "SAFE", 21.8),
    ("INV-DEMO-015", "TM-DEMO-003", "GreenBasket", "Tomato", "G", 4.2, 0.95, 13.0, "SAFE", 21.8),
    ("INV-DEMO-016", "TM-DEMO-004", "RedVine", "Tomato", "D", 4.7, 0.91, 22.0, "SAFE", 21.9),
)

DEMO_DECAY_ROWS: Final[tuple[tuple[object, ...], ...]] = (
    ("INV-DEMO-001", "2026-10-29", 20.0, "SAFE"),
    ("INV-DEMO-001", "2026-10-30", 19.0, "SAFE"),
    ("INV-DEMO-001", "2026-10-31", 18.0, "SAFE"),
    ("INV-DEMO-001", "2026-11-01", 17.0, "SAFE"),
    ("INV-DEMO-001", "2026-11-02", 16.1, "SAFE"),
    ("INV-DEMO-002", "2026-10-29", 32.0, "SAFE"),
    ("INV-DEMO-002", "2026-10-30", 31.2, "SAFE"),
    ("INV-DEMO-002", "2026-10-31", 30.4, "SAFE"),
    ("INV-DEMO-002", "2026-11-01", 29.5, "SAFE"),
    ("INV-DEMO-002", "2026-11-02", 28.7, "SAFE"),
    ("INV-DEMO-003", "2026-10-29", 12.5, "WARNING"),
    ("INV-DEMO-003", "2026-10-30", 11.4, "WARNING"),
    ("INV-DEMO-003", "2026-10-31", 10.3, "WARNING"),
    ("INV-DEMO-003", "2026-11-01", 9.2, "WARNING"),
    ("INV-DEMO-003", "2026-11-02", 8.2, "WARNING"),
    ("INV-DEMO-004", "2026-10-29", 25.0, "SAFE"),
    ("INV-DEMO-004", "2026-10-30", 24.2, "SAFE"),
    ("INV-DEMO-004", "2026-10-31", 23.4, "SAFE"),
    ("INV-DEMO-004", "2026-11-01", 22.6, "SAFE"),
    ("INV-DEMO-004", "2026-11-02", 21.8, "SAFE"),
    ("INV-DEMO-005", "2026-10-29", 19.1, "SAFE"),
    ("INV-DEMO-005", "2026-10-30", 18.1, "SAFE"),
    ("INV-DEMO-005", "2026-10-31", 17.1, "SAFE"),
    ("INV-DEMO-005", "2026-11-01", 16.1, "SAFE"),
    ("INV-DEMO-005", "2026-11-02", 15.3, "SAFE"),
    ("INV-DEMO-006", "2026-10-29", 18.8, "SAFE"),
    ("INV-DEMO-006", "2026-10-30", 17.8, "SAFE"),
    ("INV-DEMO-006", "2026-10-31", 16.8, "SAFE"),
    ("INV-DEMO-006", "2026-11-01", 15.9, "SAFE"),
    ("INV-DEMO-006", "2026-11-02", 15.0, "SAFE"),
    ("INV-DEMO-007", "2026-10-29", 20.2, "SAFE"),
    ("INV-DEMO-007", "2026-10-30", 19.3, "SAFE"),
    ("INV-DEMO-007", "2026-10-31", 18.4, "SAFE"),
    ("INV-DEMO-007", "2026-11-01", 17.6, "SAFE"),
    ("INV-DEMO-007", "2026-11-02", 16.8, "SAFE"),
    ("INV-DEMO-008", "2026-10-29", 33.6, "SAFE"),
    ("INV-DEMO-008", "2026-10-30", 32.6, "SAFE"),
    ("INV-DEMO-008", "2026-10-31", 31.7, "SAFE"),
    ("INV-DEMO-008", "2026-11-01", 30.7, "SAFE"),
    ("INV-DEMO-008", "2026-11-02", 29.8, "SAFE"),
    ("INV-DEMO-009", "2026-10-29", 30.2, "SAFE"),
    ("INV-DEMO-009", "2026-10-30", 29.2, "SAFE"),
    ("INV-DEMO-009", "2026-10-31", 28.3, "SAFE"),
    ("INV-DEMO-009", "2026-11-01", 27.3, "SAFE"),
    ("INV-DEMO-009", "2026-11-02", 26.4, "SAFE"),
    ("INV-DEMO-010", "2026-10-29", 35.8, "SAFE"),
    ("INV-DEMO-010", "2026-10-30", 34.8, "SAFE"),
    ("INV-DEMO-010", "2026-10-31", 33.8, "SAFE"),
    ("INV-DEMO-010", "2026-11-01", 32.8, "SAFE"),
    ("INV-DEMO-010", "2026-11-02", 31.8, "SAFE"),
    ("INV-DEMO-011", "2026-10-29", 13.0, "WARNING"),
    ("INV-DEMO-011", "2026-10-30", 11.9, "WARNING"),
    ("INV-DEMO-011", "2026-10-31", 10.9, "WARNING"),
    ("INV-DEMO-011", "2026-11-01", 9.9, "WARNING"),
    ("INV-DEMO-011", "2026-11-02", 8.9, "WARNING"),
    ("INV-DEMO-012", "2026-10-29", 12.0, "WARNING"),
    ("INV-DEMO-012", "2026-10-30", 10.9, "WARNING"),
    ("INV-DEMO-012", "2026-10-31", 9.9, "WARNING"),
    ("INV-DEMO-012", "2026-11-01", 8.8, "WARNING"),
    ("INV-DEMO-012", "2026-11-02", 7.8, "WARNING"),
    ("INV-DEMO-013", "2026-10-29", 13.5, "WARNING"),
    ("INV-DEMO-013", "2026-10-30", 12.5, "WARNING"),
    ("INV-DEMO-013", "2026-10-31", 11.5, "WARNING"),
    ("INV-DEMO-013", "2026-11-01", 10.5, "WARNING"),
    ("INV-DEMO-013", "2026-11-02", 9.5, "WARNING"),
    ("INV-DEMO-014", "2026-10-29", 26.0, "SAFE"),
    ("INV-DEMO-014", "2026-10-30", 24.9, "SAFE"),
    ("INV-DEMO-014", "2026-10-31", 23.9, "SAFE"),
    ("INV-DEMO-014", "2026-11-01", 22.8, "SAFE"),
    ("INV-DEMO-014", "2026-11-02", 21.8, "SAFE"),
    ("INV-DEMO-015", "2026-10-29", 25.8, "SAFE"),
    ("INV-DEMO-015", "2026-10-30", 24.8, "SAFE"),
    ("INV-DEMO-015", "2026-10-31", 23.8, "SAFE"),
    ("INV-DEMO-015", "2026-11-01", 22.8, "SAFE"),
    ("INV-DEMO-015", "2026-11-02", 21.8, "SAFE"),
    ("INV-DEMO-016", "2026-10-29", 25.9, "SAFE"),
    ("INV-DEMO-016", "2026-10-30", 24.9, "SAFE"),
    ("INV-DEMO-016", "2026-10-31", 23.9, "SAFE"),
    ("INV-DEMO-016", "2026-11-01", 22.9, "SAFE"),
    ("INV-DEMO-016", "2026-11-02", 21.9, "SAFE"),
)

INVENTORY_TABLE_SQL: Final[str] = """
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
)
"""

MIGRATIONS_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

DECAY_TABLE_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS inventory_decay (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    days_remaining REAL NOT NULL CHECK (days_remaining >= 0),
    status TEXT NOT NULL CHECK (status IN ('Pending', 'SAFE', 'WARNING', 'CRITICAL')),
    UNIQUE (inventory_id, recorded_at),
    FOREIGN KEY (inventory_id) REFERENCES inventory(id) ON DELETE CASCADE
)
"""

INDEXES_SQL: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS idx_inventory_variety ON inventory(variety)",
    "CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory(status)",
    "CREATE INDEX IF NOT EXISTS idx_inventory_decay_recorded_at "
    "ON inventory_decay(recorded_at)",
    "CREATE INDEX IF NOT EXISTS idx_inventory_decay_inventory_id "
    "ON inventory_decay(inventory_id)",
)


def validate_columns(columns: list[str] | tuple[str, ...]) -> None:
    missing = sorted(set(REQUIRED_COLUMNS) - set(columns))
    if missing:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(missing)
        )