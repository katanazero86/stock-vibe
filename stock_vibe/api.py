from __future__ import annotations

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from stock_vibe.config import AppConfig, MARKETS, list_market_options
from stock_vibe.service import DashboardData, DashboardService


app = FastAPI(title="Stock Vibe API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_service(market: str) -> DashboardService:
    if market not in MARKETS:
        raise HTTPException(status_code=400, detail=f"Unsupported market '{market}'.")
    config = AppConfig(market_key=market)
    config.ensure_directories()
    return DashboardService(config)


def serialize_dashboard_data(data: DashboardData, market: str) -> dict[str, object]:
    market_config = MARKETS[market]
    if data.frame is None or data.frame.empty:
        return {
            "market": {
                "key": market_config.key,
                "label": market_config.label,
                "short_label": market_config.short_label,
                "region_label": market_config.region_label,
                "currency_code": market_config.currency_code,
                "target_url": market_config.target_url,
            },
            "markets": list_market_options(),
            "source": data.source,
            "message": data.message,
            "summary": None,
            "rows": [],
        }

    frame = data.frame.copy()
    frame["rank"] = frame["rank"].astype(int)
    summary = {
        "rows": int(len(frame)),
        "gainers": int((frame["change_percent"] >= 0).sum()),
        "losers": int((frame["change_percent"] < 0).sum()),
        "average_change_percent": round(float(frame["change_percent"].mean()), 2),
        "last_crawl_timestamp": str(frame["crawl_timestamp"].iloc[0]),
    }

    return {
        "market": {
            "key": market_config.key,
            "label": market_config.label,
            "short_label": market_config.short_label,
            "region_label": market_config.region_label,
            "currency_code": market_config.currency_code,
            "target_url": market_config.target_url,
        },
        "markets": list_market_options(),
        "source": data.source,
        "message": data.message,
        "summary": summary,
        "rows": frame.to_dict(orient="records"),
    }


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/markets")
def get_markets() -> dict[str, object]:
    return {"markets": list_market_options()}


@app.get("/api/snapshot")
def get_snapshot(market: str = "us") -> dict[str, object]:
    return serialize_dashboard_data(get_service(market).load_cached(), market)


@app.post("/api/refresh")
def refresh_snapshot(market: str = "us") -> dict[str, object]:
    return serialize_dashboard_data(get_service(market).refresh(), market)
