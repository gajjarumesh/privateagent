"""Technical indicators for trading analysis."""

import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for market analysis."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with price data.

        Args:
            data: DataFrame with OHLCV columns
        """
        self.data = data
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that required columns exist."""
        required = ["Open", "High", "Low", "Close", "Volume"]
        missing = [col for col in required if col not in self.data.columns]

        if missing:
            # Try lowercase
            for col in missing:
                if col.lower() in self.data.columns:
                    self.data = self.data.rename(columns={col.lower(): col})

    def calculate(self, indicator: str, period: int = 14) -> Any:
        """Calculate a specific indicator."""
        indicator_map = {
            "sma": self.sma,
            "ema": self.ema,
            "rsi": self.rsi,
            "macd": self.macd,
            "bollinger": self.bollinger_bands,
            "atr": self.atr,
        }

        if indicator not in indicator_map:
            raise ValueError(f"Unknown indicator: {indicator}")

        return indicator_map[indicator](period)

    def sma(self, period: int = 20) -> Dict[str, Any]:
        """Calculate Simple Moving Average."""
        if len(self.data) < period:
            return {"error": "Insufficient data"}

        sma = self.data["Close"].rolling(window=period).mean()

        return {
            "name": f"SMA({period})",
            "current": round(sma.iloc[-1], 4) if not pd.isna(sma.iloc[-1]) else None,
            "previous": round(sma.iloc[-2], 4) if len(sma) > 1 and not pd.isna(sma.iloc[-2]) else None,
            "trend": "up" if sma.iloc[-1] > sma.iloc[-2] else "down" if len(sma) > 1 else "neutral",
        }

    def ema(self, period: int = 20) -> Dict[str, Any]:
        """Calculate Exponential Moving Average."""
        if len(self.data) < period:
            return {"error": "Insufficient data"}

        ema = self.data["Close"].ewm(span=period, adjust=False).mean()

        return {
            "name": f"EMA({period})",
            "current": round(ema.iloc[-1], 4) if not pd.isna(ema.iloc[-1]) else None,
            "previous": round(ema.iloc[-2], 4) if len(ema) > 1 and not pd.isna(ema.iloc[-2]) else None,
            "trend": "up" if ema.iloc[-1] > ema.iloc[-2] else "down" if len(ema) > 1 else "neutral",
        }

    def rsi(self, period: int = 14) -> Dict[str, Any]:
        """Calculate Relative Strength Index."""
        if len(self.data) < period + 1:
            return {"error": "Insufficient data"}

        delta = self.data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_rsi = rsi.iloc[-1]

        # Determine signal
        if current_rsi >= 70:
            signal = "overbought"
        elif current_rsi <= 30:
            signal = "oversold"
        else:
            signal = "neutral"

        return {
            "name": f"RSI({period})",
            "value": round(current_rsi, 2) if not pd.isna(current_rsi) else None,
            "signal": signal,
            "overbought_threshold": 70,
            "oversold_threshold": 30,
        }

    def macd(self, period: int = 12) -> Dict[str, Any]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        fast_period = period
        slow_period = period * 2 + 2  # Default: 26
        signal_period = 9

        if len(self.data) < slow_period:
            return {"error": "Insufficient data"}

        fast_ema = self.data["Close"].ewm(span=fast_period, adjust=False).mean()
        slow_ema = self.data["Close"].ewm(span=slow_period, adjust=False).mean()

        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_hist = histogram.iloc[-1]

        # Determine signal
        if current_macd > current_signal:
            trend = "bullish"
        else:
            trend = "bearish"

        return {
            "name": "MACD",
            "macd": round(current_macd, 4) if not pd.isna(current_macd) else None,
            "signal": round(current_signal, 4) if not pd.isna(current_signal) else None,
            "histogram": round(current_hist, 4) if not pd.isna(current_hist) else None,
            "trend": trend,
            "settings": f"({fast_period}, {slow_period}, {signal_period})",
        }

    def bollinger_bands(self, period: int = 20) -> Dict[str, Any]:
        """Calculate Bollinger Bands."""
        if len(self.data) < period:
            return {"error": "Insufficient data"}

        sma = self.data["Close"].rolling(window=period).mean()
        std = self.data["Close"].rolling(window=period).std()

        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        current_price = self.data["Close"].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_sma = sma.iloc[-1]

        # Determine position
        band_width = current_upper - current_lower
        position = (current_price - current_lower) / band_width if band_width > 0 else 0.5

        if position > 0.8:
            signal = "near_upper"
        elif position < 0.2:
            signal = "near_lower"
        else:
            signal = "middle"

        return {
            "name": f"Bollinger({period})",
            "upper": round(current_upper, 4) if not pd.isna(current_upper) else None,
            "middle": round(current_sma, 4) if not pd.isna(current_sma) else None,
            "lower": round(current_lower, 4) if not pd.isna(current_lower) else None,
            "position": round(position, 2),
            "signal": signal,
        }

    def atr(self, period: int = 14) -> Dict[str, Any]:
        """Calculate Average True Range (volatility indicator)."""
        if len(self.data) < period + 1:
            return {"error": "Insufficient data"}

        high = self.data["High"]
        low = self.data["Low"]
        close = self.data["Close"].shift(1)

        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        current_atr = atr.iloc[-1]
        current_price = self.data["Close"].iloc[-1]

        # ATR as percentage of price
        atr_percent = (current_atr / current_price) * 100 if current_price > 0 else 0

        # Volatility assessment
        if atr_percent > 5:
            volatility = "high"
        elif atr_percent > 2:
            volatility = "moderate"
        else:
            volatility = "low"

        return {
            "name": f"ATR({period})",
            "value": round(current_atr, 4) if not pd.isna(current_atr) else None,
            "percent": round(atr_percent, 2),
            "volatility": volatility,
        }

    def calculate_all(self) -> Dict[str, Any]:
        """Calculate all indicators with default settings."""
        return {
            "sma_20": self.sma(20),
            "ema_20": self.ema(20),
            "rsi_14": self.rsi(14),
            "macd": self.macd(12),
            "bollinger_20": self.bollinger_bands(20),
            "atr_14": self.atr(14),
        }
