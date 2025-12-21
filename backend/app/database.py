import json
import duckdb

from pathlib import Path
from typing import List, Dict, Any


class MetricsDatabase:
    """DuckDB class for a DuckBD database storing training metrics for the model leaderboard."""

    def __init__(self, database_path: Path):
        self.connection = duckdb.connect(str(database_path))
        self._create_table()

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
