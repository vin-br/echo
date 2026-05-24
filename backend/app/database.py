import json
import duckdb

from pathlib import Path
from typing import Any


class MetricsDatabase:
    """DuckDB class for a DuckBD database storing training metrics for the model leaderboard."""

    def __init__(self, database_path: Path):
        self.connection = duckdb.connect(str(database_path))
        self._create_table()
        self._create_latency_table()

    def _create_table(self):
        """Create single leaderboard table."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard (
                model VARCHAR,
                batch_size INTEGER,
                image_size INTEGER,
                epochs INTEGER,
                lr DOUBLE,
                test_acc DOUBLE,
                val_acc DOUBLE,
                best_epoch INTEGER,
                macro_f1 DOUBLE,
                per_class_json VARCHAR,
                PRIMARY KEY (model, batch_size, image_size, epochs, lr)
            )
        """
        )
        # Migrate: add columns if missing (existing databases)
        for col, dtype in [("macro_f1", "DOUBLE"), ("per_class_json", "VARCHAR")]:
            try:
                self.connection.execute(f"ALTER TABLE leaderboard ADD COLUMN {col} {dtype}")
            except duckdb.CatalogException:
                pass

    def _create_latency_table(self):
        """Create table for inference latency measurements."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS latency (
                id INTEGER PRIMARY KEY,
                ms DOUBLE NOT NULL
            )
        """
        )

    def ingest_json(self, json_path: Path):
        """Load a training result JSON into the database."""
        with open(json_path) as f:
            data = json.load(f)

        config = data["config"]
        per_class = data.get("per_class_metrics", {})
        macro_f1 = per_class.get("macro_f1")
        per_class_json = json.dumps(per_class.get("per_class", {})) if per_class else None

        self.connection.execute(
            """
            INSERT OR REPLACE INTO leaderboard
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                config["name"],
                config["batch_size"],
                config["image_size"],
                config["epochs"],
                config["lr"],
                data["test_metrics"]["acc"],
                data["val_metrics"]["acc"],
                data["best_epoch"],
                macro_f1,
                per_class_json,
            ],
        )

    def get_metrics(self) -> list[dict[str, Any]]:
        """Retrieve all entries sorted by test accuracy."""
        result = self.connection.execute(
            """
            SELECT * FROM leaderboard
            ORDER BY test_acc DESC
        """
        ).fetchall()

        columns = [
            "model",
            "batch_size",
            "image_size",
            "epochs",
            "lr",
            "test_acc",
            "val_acc",
            "best_epoch",
            "macro_f1",
            "per_class_json",
        ]
        rows = []
        for row in result:
            entry = dict(zip(columns, row))
            # Parse per_class_json back to dict for the API response
            raw = entry.pop("per_class_json", None)
            per_class = json.loads(raw) if raw else None
            entry["per_class"] = per_class
            # Compute macro recall from per-class data
            if per_class:
                recalls = [m["recall"] for m in per_class.values() if isinstance(m, dict) and "recall" in m]
                entry["macro_recall"] = sum(recalls) / len(recalls) if recalls else None
            else:
                entry["macro_recall"] = None
            rows.append(entry)
        return rows

    def close(self):
        """Close database connection."""
        self.connection.close()

    # ------------------------------------------------------------------
    # Inference latency (rolling window of last 100 measurements)
    # ------------------------------------------------------------------

    def record_latency(self, ms: float) -> None:
        """Append a latency measurement, keeping only the last 100 rows."""
        next_id = self.connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM latency").fetchone()[0]
        self.connection.execute("INSERT INTO latency VALUES (?, ?)", [next_id, ms])
        # Trim to last 100
        self.connection.execute(
            "DELETE FROM latency WHERE id <= (SELECT MAX(id) - 100 FROM latency)"
        )

    def get_latency(self) -> dict[str, Any]:
        """Return average latency and count from stored measurements."""
        row = self.connection.execute(
            "SELECT AVG(ms), COUNT(*) FROM latency"
        ).fetchone()
        if row is None or row[1] == 0:
            return {"avg_ms": None, "count": 0}
        return {"avg_ms": round(row[0], 1), "count": row[1]}
