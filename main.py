"""
main.py
Point d'entree FastAPI. Expose une API simple pour recuperer
le prix, l'analyse technique, et la decision finale.

Lancer avec : uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from market_data import get_current_price, get_klines
from technical import analyze

app = FastAPI(title="Bitcoin Futures Analyzer")

# Autorise le frontend (servi separement) a appeler cette API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/price")
def api_price():
    return {"symbol": "BTCUSDT", "price": get_current_price()}


@app.get("/api/technical")
def api_technical(interval: str = "1h", limit: int = 250):
    candles = get_klines(interval=interval, limit=limit)
    return analyze(candles)


@app.get("/api/decision")
def api_decision():
    candles = get_klines(interval="1h", limit=250)
    technical = analyze(candles)

    score = technical["technical_score"]
    if score > 0.3:
        decision = "LONG"
    elif score < -0.3:
        decision = "SHORT"
    else:
        decision = "ATTENDRE"

    return {
        "decision": decision,
        "confidence": round(abs(score) * 100, 1),
        "technical": technical,
    }
