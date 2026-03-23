from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import pandas as pd

from stock_vibe.models import StockSnapshot


class SnapshotStorage:
    def __init__(self, dataset_path: Path, log_path: Path) -> None:
        self.dataset_path = dataset_path
        self.log_path = log_path

    def save(self, snapshots: list[StockSnapshot]) -> pd.DataFrame:
        frame = pd.DataFrame([snapshot.to_dict() for snapshot in snapshots])
        frame.to_csv(self.dataset_path, index=False)
        self.append_log(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "success",
                "rows": len(frame),
            }
        )
        return frame

    def load_latest(self) -> pd.DataFrame | None:
        if not self.dataset_path.exists():
            return None
        return pd.read_csv(
            self.dataset_path,
            dtype={
                "symbol": "string",
                "company_name": "string",
                "market": "string",
                "quote_currency": "string",
                "source_url": "string",
                "crawl_timestamp": "string",
            },
        )

    def append_log(self, entry: dict[str, object]) -> None:
        existing: list[dict[str, object]] = []
        if self.log_path.exists():
            existing = json.loads(self.log_path.read_text(encoding="utf-8"))
        existing.append(entry)
        self.log_path.write_text(json.dumps(existing[-50:], ensure_ascii=True, indent=2), encoding="utf-8")

    def log_failure(self, reason: str, detail: str) -> None:
        self.append_log(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "status": "failure",
                "reason": reason,
                "detail": detail,
            }
        )
