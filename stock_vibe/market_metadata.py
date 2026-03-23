from __future__ import annotations

from datetime import datetime, timedelta
from io import StringIO
import json
from pathlib import Path

import pandas as pd
import requests


KOSPI_LIST_URL = (
    "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=stockMkt"
)


class MarketMetadataError(RuntimeError):
    """Raised when market metadata cannot be loaded."""


def load_kospi_company_map(cache_path: Path) -> dict[str, str]:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if _is_fresh(cache_path):
        return json.loads(cache_path.read_text(encoding="utf-8"))

    response = requests.get(KOSPI_LIST_URL, timeout=30)
    response.raise_for_status()
    response.encoding = "euc-kr"
    tables = pd.read_html(StringIO(response.text))
    if not tables:
        raise MarketMetadataError("KRX corp list did not return any tables.")

    frame = tables[0].copy()
    frame["종목코드"] = frame["종목코드"].astype(str).str.zfill(6)
    company_map = dict(zip(frame["종목코드"], frame["회사명"], strict=False))
    cache_path.write_text(json.dumps(company_map, ensure_ascii=False, indent=2), encoding="utf-8")
    return company_map


def _is_fresh(cache_path: Path) -> bool:
    if not cache_path.exists():
        return False
    modified_at = datetime.fromtimestamp(cache_path.stat().st_mtime)
    return datetime.now() - modified_at < timedelta(hours=24)
