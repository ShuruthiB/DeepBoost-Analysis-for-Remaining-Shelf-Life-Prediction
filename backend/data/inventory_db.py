from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .schema import (
    DECAY_TABLE_SQL,
    DEMO_DECAY_ROWS,
    DEMO_INVENTORY_ROWS,
    INDEXES_SQL,
    INVENTORY_TABLE_SQL,
    MIGRATIONS_TABLE_SQL,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = (PROJECT_ROOT / "backend" / "inventory.sqlite3").resolve()


def _production_seed_rows(rows: tuple[tuple[object, ...], ...]) -> list[tuple[object, ...]]:
    return [
        tuple(value.replace("-DEMO", "") if isinstance(value, str) else value for value in row)
        for row in rows
    ]


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode = DELETE")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def initialize_inventory_database() -> None:
    with _connect() as connection:
        connection.execute(MIGRATIONS_TABLE_SQL)
        existing = connection.execute("PRAGMA table_info(inventory)").fetchall()
        if existing and any(row["name"] == "days" for row in existing):
            days_type = next(row["type"] for row in existing if row["name"] == "days")
            nullable_supplier = next(
                row["notnull"] == 0 for row in existing if row["name"] == "supplier"
            )
            if days_type.upper() != "REAL" or nullable_supplier:
                connection.execute("ALTER TABLE inventory RENAME TO inventory_legacy")
                connection.execute(INVENTORY_TABLE_SQL)
                connection.execute(
                    """
                    INSERT INTO inventory
                    (id, batch, supplier, variety, shelf, ph, moisture, temp, status, days)
                    SELECT id, batch, COALESCE(supplier, 'Unassigned'), variety,
                           COALESCE(shelf, 'Unassigned'), ph, moisture, temp, status,
                           CASE WHEN days IN ('--', '') THEN NULL ELSE CAST(days AS REAL) END
                    FROM inventory_legacy
                    """
                )
                connection.execute("DROP TABLE inventory_legacy")
        else:
            connection.execute(INVENTORY_TABLE_SQL)
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (2)"
        )
        if not connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = 3"
        ).fetchone():
            connection.executemany(
                """
                INSERT OR IGNORE INTO inventory
                (id, batch, supplier, variety, shelf, ph, moisture, temp, status, days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _production_seed_rows(DEMO_INVENTORY_ROWS),
            )
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (3)"
            )
        connection.execute(DECAY_TABLE_SQL)
        for statement in INDEXES_SQL:
            connection.execute(statement)
        if not connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = 4"
        ).fetchone():
            connection.executemany(
                """
                INSERT OR IGNORE INTO inventory_decay
                (inventory_id, recorded_at, days_remaining, status)
                VALUES (?, ?, ?, ?)
                """,
                _production_seed_rows(DEMO_DECAY_ROWS),
            )
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (4)"
            )
        if not connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = 5"
        ).fetchone():
            connection.executemany(
                """
                INSERT OR IGNORE INTO inventory
                (id, batch, supplier, variety, shelf, ph, moisture, temp, status, days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _production_seed_rows(DEMO_INVENTORY_ROWS[4:]),
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO inventory_decay
                (inventory_id, recorded_at, days_remaining, status)
                VALUES (?, ?, ?, ?)
                """,
                _production_seed_rows(DEMO_DECAY_ROWS[20:]),
            )
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (5)"
            )
        if not connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = 6"
        ).fetchone():
            connection.execute("PRAGMA defer_foreign_keys = ON")
            connection.execute(
                "UPDATE inventory_decay SET inventory_id = REPLACE(inventory_id, '-DEMO', '')"
            )
            connection.execute(
                "UPDATE inventory SET id = REPLACE(id, '-DEMO', ''), batch = REPLACE(batch, '-DEMO', '')"
            )
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (6)"
            )


def list_inventory() -> list[dict[str, Any]]:
    initialize_inventory_database()
    with _connect() as connection:
        return [dict(row) for row in connection.execute(
            "SELECT id, batch, supplier, variety, shelf, ph, moisture, temp, status, days "
            "FROM inventory ORDER BY rowid"
        )]


def create_inventory(item: dict[str, Any]) -> dict[str, Any]:
    initialize_inventory_database()
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO inventory
            (id, batch, supplier, variety, shelf, ph, moisture, temp, status, days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["id"], item["batch"], item["supplier"], item["variety"],
                item["shelf"], item["ph"], item["moisture"], item["temp"],
                item.get("status", "Pending"), item.get("days"),
            ),
        )
    return next(row for row in list_inventory() if row["id"] == item["id"])


def update_inventory(item_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
    initialize_inventory_database()
    immutable_fields = set(values) & {"status", "days"}
    if immutable_fields:
        raise ValueError("Saved status and shelf-life prediction cannot be changed.")
    allowed = {key: values[key] for key in ("temp",) if key in values}
    if not allowed:
        raise ValueError("No supported inventory fields were supplied.")
    assignments = ", ".join(f"{key} = ?" for key in allowed)
    with _connect() as connection:
        cursor = connection.execute(
            f"UPDATE inventory SET {assignments} WHERE id = ?",
            (*allowed.values(), item_id),
        )
        if cursor.rowcount == 0:
            return None
    return next(row for row in list_inventory() if row["id"] == item_id)


def list_decay_history() -> list[dict[str, Any]]:
    initialize_inventory_database()
    with _connect() as connection:
        return [
            dict(row)
            for row in connection.execute(
                """
                SELECT inventory_id, recorded_at, days_remaining, status
                FROM inventory_decay
                ORDER BY recorded_at, inventory_id
                """
            )
        ]
