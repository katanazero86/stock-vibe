from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class StockSnapshot:
    rank: int
    symbol: str
    company_name: str
    current_price: float
    change_percent: float
    volume: float | None
    turnover: float | None
    market: str
    quote_currency: str
    source_url: str
    crawl_timestamp: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
