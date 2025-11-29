"""Market trading analyst module."""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd

from app.core.llm_engine import LLMEngine
from app.modules.trading.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

# Yahoo Finance is used for market data (free API)
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance not installed. Trading features will be limited.")


class TradingAnalyst:
    """Market trading analysis assistant."""

    DISCLAIMER = (
        "⚠️ DISCLAIMER: This analysis is for informational and educational purposes only. "
        "It does not constitute financial advice, investment advice, or a recommendation "
        "to buy or sell any security. Always do your own research and consult with a "
        "qualified financial advisor before making investment decisions."
    )

    def __init__(self, llm: Optional[LLMEngine] = None):
        """Initialize trading analyst."""
        self.llm = llm or LLMEngine()

    async def process(
        self, message: str, context: str = ""
    ) -> Dict[str, Any]:
        """
        Process a trading analysis request.

        Args:
            message: User's request
            context: Conversation context

        Returns:
            Dict with response and metadata
        """
        system_prompt = """You are a market trading analyst assistant.
You help users understand technical analysis, market indicators, and trading concepts.
You provide educational information about market analysis.

IMPORTANT: Always include the disclaimer that this is not financial advice.
Be objective and present both bullish and bearish perspectives when relevant.
Explain technical indicators in an accessible way."""

        prompt = f"""Previous context:
{context}

User: {message}

Provide helpful analysis including:
1. Clear explanation of relevant concepts
2. Technical indicator interpretation if applicable
3. Both bullish and bearish considerations
4. Risk factors to consider

Always end with the disclaimer that this is educational only, not financial advice.

Analysis:"""

        result = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
        )

        # Append disclaimer if not already present
        response = result.get("response", "")
        if "disclaimer" not in response.lower() and "not financial advice" not in response.lower():
            response += f"\n\n{self.DISCLAIMER}"
            result["response"] = response

        return result

    async def fetch_data(
        self,
        symbol: str,
        period: str = "1mo",
    ) -> Optional[pd.DataFrame]:
        """Fetch market data for a symbol."""
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance not available")
            return None

        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)

            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return None

            return data

        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            return None

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current quote for a symbol."""
        if not YFINANCE_AVAILABLE:
            return None

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", symbol)),
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "open": info.get("open") or info.get("regularMarketOpen"),
                "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "day_low": info.get("dayLow") or info.get("regularMarketDayLow"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "currency": info.get("currency", "USD"),
            }

        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {str(e)}")
            return None

    async def analyze(
        self,
        symbol: str,
        period: str = "1mo",
        indicators: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform technical analysis on a symbol.

        Args:
            symbol: Stock/crypto symbol
            period: Time period for analysis
            indicators: List of indicators to calculate

        Returns:
            Analysis results
        """
        indicators = indicators or ["sma", "rsi", "macd"]

        # Fetch data
        data = await self.fetch_data(symbol, period)
        if data is None or data.empty:
            raise ValueError(f"Unable to fetch data for {symbol}")

        # Get current quote
        quote = await self.get_quote(symbol)
        current_price = quote.get("price") if quote else None

        # Calculate indicators
        tech_indicators = TechnicalIndicators(data)
        indicator_results = {}

        for ind in indicators:
            try:
                indicator_results[ind] = tech_indicators.calculate(ind)
            except Exception as e:
                logger.warning(f"Failed to calculate {ind}: {str(e)}")
                indicator_results[ind] = {"error": str(e)}

        # Generate recommendation based on indicators
        recommendation = self._generate_recommendation(indicator_results)

        # Build analysis summary
        analysis = {
            "period": period,
            "data_points": len(data),
            "price_range": {
                "high": round(data["High"].max(), 4),
                "low": round(data["Low"].min(), 4),
            },
            "trend": self._determine_trend(data),
        }

        return {
            "symbol": symbol,
            "current_price": current_price,
            "analysis": analysis,
            "indicators": indicator_results,
            "recommendation": recommendation,
            "disclaimer": self.DISCLAIMER,
        }

    def _determine_trend(self, data: pd.DataFrame) -> str:
        """Determine overall trend from price data."""
        if len(data) < 2:
            return "insufficient_data"

        first_close = data["Close"].iloc[0]
        last_close = data["Close"].iloc[-1]
        change_percent = ((last_close - first_close) / first_close) * 100

        if change_percent > 5:
            return "strong_uptrend"
        elif change_percent > 2:
            return "uptrend"
        elif change_percent < -5:
            return "strong_downtrend"
        elif change_percent < -2:
            return "downtrend"
        else:
            return "sideways"

    def _generate_recommendation(self, indicators: Dict[str, Any]) -> str:
        """Generate recommendation based on indicators."""
        bullish_signals = 0
        bearish_signals = 0

        # Check RSI
        rsi = indicators.get("rsi", {})
        if rsi.get("signal") == "oversold":
            bullish_signals += 1
        elif rsi.get("signal") == "overbought":
            bearish_signals += 1

        # Check MACD
        macd = indicators.get("macd", {})
        if macd.get("trend") == "bullish":
            bullish_signals += 1
        elif macd.get("trend") == "bearish":
            bearish_signals += 1

        # Check Bollinger
        bollinger = indicators.get("bollinger", {})
        if bollinger.get("signal") == "near_lower":
            bullish_signals += 1
        elif bollinger.get("signal") == "near_upper":
            bearish_signals += 1

        # Check SMA/EMA trends
        for key in ["sma", "ema"]:
            ind = indicators.get(key, {})
            if ind.get("trend") == "up":
                bullish_signals += 1
            elif ind.get("trend") == "down":
                bearish_signals += 1

        # Generate recommendation
        if bullish_signals > bearish_signals + 1:
            return "Indicators suggest bullish momentum. Consider this for research only."
        elif bearish_signals > bullish_signals + 1:
            return "Indicators suggest bearish momentum. Consider this for research only."
        else:
            return "Mixed signals. Indicators are not showing a clear direction."
