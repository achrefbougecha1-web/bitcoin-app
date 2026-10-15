"""
market_data.py
Recupere le prix, les bougies (klines) et le volume du bitcoin
depuis l'API publique de Binance (pas de cle API necessaire pour les donnees de marche).
"""

import requests

BINANCE_BASE_URL = "https://api.binance.com"


def get_current_price(symbol: str = "BTCUSDT") -> float:
    """Retourne le dernier prix connu pour la paire donnee."""
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": symbol}, timeout=10)
    response.raise_for_status()
    data = response.json()
    return float(data["price"])


def get_klines(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 200):
    """
    Recupere les bougies (klines).
    interval possibles : 15m, 1h, 4h, 1d
    Retourne une liste de dictionnaires faciles a utiliser.
    """
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()

    candles = []
    for entry in raw:
        candles.append({
            "open_time": entry[0],
            "open": float(entry[1]),
            "high": float(entry[2]),
            "low": float(entry[3]),
            "close": float(entry[4]),
            "volume": float(entry[5]),
            "close_time": entry[6],
        })
    return candles


def get_multi_timeframe(symbol: str = "BTCUSDT"):
    """Recupere les bougies sur plusieurs echelles de temps d'un coup."""
    return {
        "15m": get_klines(symbol, "15m"),
        "1h": get_klines(symbol, "1h"),
        "4h": get_klines(symbol, "4h"),
        "1d": get_klines(symbol, "1d"),
    }


if __name__ == "__main__":
    price = get_current_price()
    print(f"Prix BTC/USDT actuel : {price}")

    candles = get_klines(interval="1h", limit=5)
    print("5 dernieres bougies 1h :")
    for c in candles:
        print(c)
