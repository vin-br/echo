import json
import duckdb

from pathlib import Path
from typing import List, Dict, Any


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
                PRIMARY KEY (model, batch_size, image_size, epochs, lr)
            )
        """
        )

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
        self.connection.execute(
            """
            INSERT OR REPLACE INTO leaderboard
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
            ],
        )

    def get_metrics(self) -> List[Dict[str, Any]]:
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
        ]
        return [dict(zip(columns, row)) for row in result]

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

    def get_latency(self) -> Dict[str, Any]:
        """Return average latency and count from stored measurements."""
        row = self.connection.execute(
            "SELECT AVG(ms), COUNT(*) FROM latency"
        ).fetchone()
        if row is None or row[1] == 0:
            return {"avg_ms": None, "count": 0}
        return {"avg_ms": round(row[0], 1), "count": row[1]}
