"""Tests for specialized modules."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import numpy as np

from app.modules.developer.assistant import DeveloperAssistant
from app.modules.trading.analyst import TradingAnalyst
from app.modules.trading.indicators import TechnicalIndicators
from app.modules.research.engine import ResearchEngine
from app.modules.research.rag import RAGStore
from app.security import sanitize_input, validate_code_safety


class TestDeveloperAssistant:
    """Tests for DeveloperAssistant."""

    def test_detect_request_type_debugging(self):
        """Test debugging request detection."""
        assistant = DeveloperAssistant()

        assert assistant._detect_request_type("debug this code") == "debugging"
        assert assistant._detect_request_type("fix the error") == "debugging"
        assert assistant._detect_request_type("there's a bug") == "debugging"

    def test_detect_request_type_generation(self):
        """Test generation request detection."""
        assistant = DeveloperAssistant()

        assert assistant._detect_request_type("generate a function") == "generation"
        assert assistant._detect_request_type("create a class") == "generation"
        assert assistant._detect_request_type("write code for") == "generation"

    def test_detect_request_type_review(self):
        """Test review request detection."""
        assistant = DeveloperAssistant()

        assert assistant._detect_request_type("review this code") == "review"
        assert assistant._detect_request_type("improve this") == "review"
        assert assistant._detect_request_type("optimize the function") == "review"

    def test_detect_language(self):
        """Test language detection."""
        assistant = DeveloperAssistant()

        assert assistant._detect_language("write python code") == "python"
        assert assistant._detect_language("JavaScript function") == "javascript"
        assert assistant._detect_language("create a .py file") == "python"
        assert assistant._detect_language("generic request") == "python"  # Default

    @pytest.mark.asyncio
    async def test_process(self):
        """Test processing a development request."""
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value={
            "response": "Here's your code...",
            "tokens_used": 50,
        })

        assistant = DeveloperAssistant(llm=mock_llm)
        result = await assistant.process("Write a hello world function")

        assert "response" in result
        mock_llm.generate.assert_called_once()


class TestTechnicalIndicators:
    """Tests for TechnicalIndicators."""

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data."""
        dates = pd.date_range(start="2024-01-01", periods=50, freq="D")
        data = pd.DataFrame({
            "Open": np.random.uniform(100, 110, 50),
            "High": np.random.uniform(108, 115, 50),
            "Low": np.random.uniform(95, 102, 50),
            "Close": np.random.uniform(100, 110, 50),
            "Volume": np.random.randint(1000000, 5000000, 50),
        }, index=dates)
        # Make High always >= Open and Low always <= Open for realistic data
        data["High"] = data[["Open", "High"]].max(axis=1)
        data["Low"] = data[["Open", "Low"]].min(axis=1)
        return data

    def test_sma(self, sample_data):
        """Test SMA calculation."""
        indicators = TechnicalIndicators(sample_data)
        result = indicators.sma(20)

        assert "name" in result
        assert result["name"] == "SMA(20)"
        assert "current" in result
        assert result["current"] is not None

    def test_ema(self, sample_data):
        """Test EMA calculation."""
        indicators = TechnicalIndicators(sample_data)
        result = indicators.ema(20)

        assert result["name"] == "EMA(20)"
        assert result["current"] is not None

    def test_rsi(self, sample_data):
        """Test RSI calculation."""
        indicators = TechnicalIndicators(sample_data)
        result = indicators.rsi(14)

        assert result["name"] == "RSI(14)"
        assert "value" in result
        assert "signal" in result
        # RSI should be between 0 and 100
        if result["value"] is not None:
            assert 0 <= result["value"] <= 100

    def test_macd(self, sample_data):
        """Test MACD calculation."""
        indicators = TechnicalIndicators(sample_data)
        result = indicators.macd(12)

        assert result["name"] == "MACD"
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
        assert "trend" in result

    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation."""
        indicators = TechnicalIndicators(sample_data)
        result = indicators.bollinger_bands(20)

        assert "upper" in result
        assert "middle" in result
        assert "lower" in result
        # Upper should be > middle > lower
        if result["upper"] is not None and result["middle"] is not None:
            assert result["upper"] > result["middle"]
        if result["middle"] is not None and result["lower"] is not None:
            assert result["middle"] > result["lower"]

    def test_atr(self, sample_data):
        """Test ATR calculation."""
        indicators = TechnicalIndicators(sample_data)
        result = indicators.atr(14)

        assert result["name"] == "ATR(14)"
        assert "value" in result
        assert "volatility" in result

    def test_calculate_all(self, sample_data):
        """Test calculating all indicators."""
        indicators = TechnicalIndicators(sample_data)
        result = indicators.calculate_all()

        assert "sma_20" in result
        assert "ema_20" in result
        assert "rsi_14" in result
        assert "macd" in result
        assert "bollinger_20" in result
        assert "atr_14" in result


class TestTradingAnalyst:
    """Tests for TradingAnalyst."""

    def test_disclaimer_present(self):
        """Test that disclaimer is defined."""
        analyst = TradingAnalyst()
        assert "not financial advice" in analyst.DISCLAIMER.lower() or \
               "disclaimer" in analyst.DISCLAIMER.lower()

    def test_generate_recommendation(self):
        """Test recommendation generation."""
        analyst = TradingAnalyst()

        # Test with bullish indicators
        bullish_indicators = {
            "rsi": {"signal": "oversold"},
            "macd": {"trend": "bullish"},
            "sma": {"trend": "up"},
        }
        recommendation = analyst._generate_recommendation(bullish_indicators)
        assert "bullish" in recommendation.lower() or "research" in recommendation.lower()

        # Test with bearish indicators
        bearish_indicators = {
            "rsi": {"signal": "overbought"},
            "macd": {"trend": "bearish"},
            "sma": {"trend": "down"},
        }
        recommendation = analyst._generate_recommendation(bearish_indicators)
        assert "bearish" in recommendation.lower() or "research" in recommendation.lower()


class TestResearchEngine:
    """Tests for ResearchEngine."""

    @pytest.mark.asyncio
    async def test_ingest_document(self):
        """Test document ingestion."""
        engine = ResearchEngine()

        doc_id = await engine.ingest_document(
            content="This is a test document with some content.",
            source="test",
        )

        assert doc_id is not None
        assert len(engine.list_documents()) == 1

    @pytest.mark.asyncio
    async def test_query_empty(self):
        """Test querying with no documents."""
        engine = ResearchEngine()

        result = await engine.query("What is the answer?")

        assert "don't have any documents" in result["answer"].lower() or \
               len(result["sources"]) == 0

    @pytest.mark.asyncio
    async def test_query_with_documents(self):
        """Test querying with ingested documents."""
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value={
            "response": "Based on the documents, the answer is X.",
        })

        engine = ResearchEngine(llm=mock_llm)

        await engine.ingest_document(
            content="The answer to everything is 42.",
            source="hitchhikers_guide",
        )

        result = await engine.query("What is the answer?")

        assert "answer" in result

    def test_chunk_text(self):
        """Test text chunking."""
        engine = ResearchEngine()

        text = " ".join(["word"] * 1000)  # 1000 words
        chunks = engine._chunk_text(text, chunk_size=100, overlap=10)

        assert len(chunks) > 1
        # Each chunk should have approximately 100 words
        for chunk in chunks[:-1]:  # Exclude last chunk which may be smaller
            word_count = len(chunk.split())
            assert word_count <= 100


class TestRAGStore:
    """Tests for RAGStore."""

    def test_add_and_search(self):
        """Test adding chunks and searching."""
        store = RAGStore()

        store.add_chunk("Python is a programming language", "doc1")
        store.add_chunk("JavaScript runs in browsers", "doc2")
        store.add_chunk("Python can be used for web development", "doc3")

        results = store.search("Python programming", top_k=2)

        assert len(results) > 0
        # Python-related chunks should score higher
        assert any("python" in r["content"].lower() for r in results)

    def test_delete_by_doc(self):
        """Test deleting chunks by document ID."""
        store = RAGStore()

        store.add_chunk("Content 1", "doc1")
        store.add_chunk("Content 2", "doc1")
        store.add_chunk("Content 3", "doc2")

        deleted = store.delete_by_doc("doc1")

        assert deleted == 2
        assert store.chunk_count == 1

    def test_clear(self):
        """Test clearing all data."""
        store = RAGStore()

        store.add_chunk("Content", "doc1")
        store.clear()

        assert store.chunk_count == 0


class TestSecurity:
    """Tests for security utilities."""

    def test_sanitize_input(self):
        """Test input sanitization."""
        # Normal input
        assert sanitize_input("Hello world") == "Hello world"

        # Remove null bytes
        assert "\x00" not in sanitize_input("Hello\x00world")

        # Trim whitespace
        assert sanitize_input("  hello  ") == "hello"

        # Limit length
        long_input = "a" * 20000
        result = sanitize_input(long_input)
        assert len(result) <= 10000

    def test_validate_code_safety(self):
        """Test code safety validation."""
        # Safe code
        is_safe, _ = validate_code_safety("def hello():\n    print('Hello')")
        assert is_safe is True

        # Dangerous code with os.system
        is_safe, msg = validate_code_safety("os.system('rm -rf /')")
        assert is_safe is False
        assert "os.system" in msg

        # Dangerous code with eval
        is_safe, msg = validate_code_safety("result = eval(user_input)")
        assert is_safe is False
        assert "eval" in msg

        # Dangerous code with subprocess
        is_safe, msg = validate_code_safety("subprocess.run(['ls'])")
        assert is_safe is False
        assert "subprocess" in msg
