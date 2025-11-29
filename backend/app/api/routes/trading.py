"""Trading analysis API endpoints."""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.modules.trading.analyst import TradingAnalyst
from app.modules.trading.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)
router = APIRouter()

# Create trading analyst instance
trading_analyst = TradingAnalyst()


class AnalysisRequest(BaseModel):
    """Trading analysis request model."""

    symbol: str = Field(..., min_length=1, max_length=10, pattern="^[A-Z0-9]+$")
    period: str = Field(default="1mo", pattern="^(1d|5d|1mo|3mo|6mo|1y|2y|5y)$")
    indicators: List[str] = Field(
        default=["sma", "rsi", "macd"],
        description="Technical indicators to calculate",
    )


class AnalysisResponse(BaseModel):
    """Trading analysis response model."""

    symbol: str
    current_price: Optional[float]
    analysis: dict
    indicators: dict
    recommendation: str
    disclaimer: str = (
        "This is for informational purposes only and does not constitute "
        "financial advice. Always do your own research before making investment decisions."
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_symbol(request: AnalysisRequest):
    """Analyze a trading symbol with technical indicators."""
    try:
        result = await trading_analyst.analyze(
            symbol=request.symbol,
            period=request.period,
            indicators=request.indicators,
        )
        return AnalysisResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform analysis")


class IndicatorRequest(BaseModel):
    """Single indicator calculation request."""

    symbol: str = Field(..., min_length=1, max_length=10)
    indicator: str = Field(..., pattern="^(sma|ema|rsi|macd|bollinger|atr)$")
    period: int = Field(default=14, ge=2, le=200)


@router.post("/indicator")
async def calculate_indicator(request: IndicatorRequest):
    """Calculate a specific technical indicator."""
    try:
        # Fetch data
        data = await trading_analyst.fetch_data(request.symbol)
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")

        # Calculate indicator
        indicators = TechnicalIndicators(data)
        result = indicators.calculate(request.indicator, request.period)

        return {
            "symbol": request.symbol,
            "indicator": request.indicator,
            "period": request.period,
            "value": result,
            "disclaimer": "For informational purposes only.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Indicator calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate indicator")


@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """Get current quote for a symbol."""
    try:
        symbol = symbol.upper()
        if not symbol.isalnum() or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid symbol format")

        quote = await trading_analyst.get_quote(symbol)
        if quote is None:
            raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")

        return {
            **quote,
            "disclaimer": "For informational purposes only.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quote error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get quote")
