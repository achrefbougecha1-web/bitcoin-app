"""
technical.py
Calcule les indicateurs techniques classiques a partir des bougies :
RSI, MACD, moyennes mobiles, bandes de Bollinger.
Utilise pandas pour simplifier les calculs.
"""

import pandas as pd


def candles_to_dataframe(candles: list) -> pd.DataFrame:
    """Convertit la liste de bougies de market_data.py en DataFrame pandas."""
    df = pd.DataFrame(candles)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df.set_index("open_time", inplace=True)
    return df


def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """RSI classique sur la colonne 'close'."""
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
    """Retourne la ligne MACD, la ligne de signal et l'histogramme."""
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def compute_moving_averages(df: pd.DataFrame, short: int = 50, long: int = 200):
    """Moyennes mobiles simples (SMA)."""
    sma_short = df["close"].rolling(window=short).mean()
    sma_long = df["close"].rolling(window=long).mean()
    return sma_short, sma_long


def compute_bollinger_bands(df: pd.DataFrame, period: int = 20, num_std: float = 2.0):
    """Bandes de Bollinger : bande moyenne, superieure, inferieure."""
    sma = df["close"].rolling(window=period).mean()
    std = df["close"].rolling(window=period).std()

    upper_band = sma + num_std * std
    lower_band = sma - num_std * std

    return sma, upper_band, lower_band


def analyze(candles: list) -> dict:
    """
    Calcule tous les indicateurs sur une liste de bougies
    et retourne un resume avec la derniere valeur de chacun,
    plus un score simple entre -1 et 1.
    """
    df = candles_to_dataframe(candles)

    rsi = compute_rsi(df)
    macd_line, signal_line, histogram = compute_macd(df)
    sma_short, sma_long = compute_moving_averages(df)
    bb_mid, bb_upper, bb_lower = compute_bollinger_bands(df)

    last_rsi = rsi.iloc[-1]
    last_macd_hist = histogram.iloc[-1]
    last_close = df["close"].iloc[-1]
    last_sma_short = sma_short.iloc[-1]
    last_sma_long = sma_long.iloc[-1]

    score = 0
    votes = 0

    if not pd.isna(last_rsi):
        votes += 1
        if last_rsi < 30:
            score += 1
        elif last_rsi > 70:
            score -= 1

    if not pd.isna(last_macd_hist):
        votes += 1
        score += 1 if last_macd_hist > 0 else -1

    if not pd.isna(last_sma_short) and not pd.isna(last_sma_long):
        votes += 1
        score += 1 if last_sma_short > last_sma_long else -1

    final_score = score / votes if votes > 0 else 0.0

    return {
        "last_close": last_close,
        "rsi": last_rsi,
        "macd_histogram": last_macd_hist,
        "sma_short": last_sma_short,
        "sma_long": last_sma_long,
        "bollinger_mid": bb_mid.iloc[-1],
        "bollinger_upper": bb_upper.iloc[-1],
        "bollinger_lower": bb_lower.iloc[-1],
        "technical_score": round(final_score, 2),
    }


if __name__ == "__main__":
    from market_data import get_klines

    candles = get_klines(interval="1h", limit=250)
    result = analyze(candles)
    print(result)
