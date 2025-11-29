# ARIA - Adaptive Research & Intelligence Agent

<div align="center">

```
     █████╗ ██████╗ ██╗ █████╗ 
    ██╔══██╗██╔══██╗██║██╔══██╗
    ███████║██████╔╝██║███████║
    ██╔══██║██╔══██╗██║██╔══██║
    ██║  ██║██║  ██║██║██║  ██║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
```

🚀 **A powerful, fully local AI agent system with development assistance, market trading analysis, and research capabilities.**

[![100% Local AI](https://img.shields.io/badge/AI-100%25%20Local-green)](/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](/)
[![React](https://img.shields.io/badge/React-18-61DAFB)](/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](/)

</div>

---

## 🌟 Features

- **🔒 100% Local AI** - All AI processing runs on your machine via Ollama. No external API calls for AI.
- **👨‍💻 Development Assistant** - Code generation, review, debugging, and best practices
- **📈 Market Trading Analyst** - Technical indicators (RSI, MACD, Bollinger Bands), market analysis
- **🔬 Research Engine** - Web search (DuckDuckGo), document ingestion, RAG
- **📚 Learning from Feedback** - Improves responses based on your thumbs up/down ratings
- **🛡️ Security First** - Encrypted storage, input sanitization, rate limiting, audit logging

---

## 📋 Table of Contents

- [Hardware Requirements](#-hardware-requirements)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Architecture](#-architecture)

---

## 💻 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB |
| Storage | 20 GB | 50+ GB |
| GPU | Not required | Optional (CUDA for faster inference) |

**Tested Configuration:**
- AMD Ryzen 5 3500U with Radeon Vega Mobile Gfx
- 16GB RAM
- 100GB Storage

---

## ⚡ Quick Start

### One-Click Setup

```bash
# Clone the repository
git clone https://github.com/gajjarumesh/privateagent.git
cd privateagent

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

The setup script will:
1. Check system requirements
2. Install Ollama if not present
3. Pull required models (Mistral 7B Q4)
4. Set up PostgreSQL database
5. Configure environment variables
6. Start all services

### Docker Quick Start

```bash
# Clone and navigate
git clone https://github.com/gajjarumesh/privateagent.git
cd privateagent

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d
```

Access the UI at: **http://localhost:3000**

---

## 📦 Installation

### Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for local development)
- **Ollama** (for local LLM)

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Local Development

#### 1. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows
# Download from https://ollama.com/download
```

#### 2. Pull LLM Models

```bash
# Start Ollama service
ollama serve

# In another terminal, pull models
ollama pull mistral:7b-instruct-q4_K_M
```

#### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload
```

#### 4. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

#### 5. Set Up PostgreSQL

```bash
# Using Docker
docker run -d \
  --name aria-postgres \
  -e POSTGRES_USER=aria \
  -e POSTGRES_PASSWORD=aria_password \
  -e POSTGRES_DB=aria_db \
  -p 5432:5432 \
  postgres:15-alpine
```

---

## 📖 Usage Guide

### UI Overview

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 ARIA                                                    │
│  AI Agent                                                   │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│  + New Chat │  👨‍💻 Developer Assistant                       │
│             │  Code generation, debugging, best practices   │
│  Modules    │                                               │
│  ─────────  ├───────────────────────────────────────────────┤
│  💬 General │                                               │
│  👨‍💻 Developer│  👤 Write a Python function to sort a list  │
│  📈 Trading │                                               │
│  🔬 Research│  🤖 Here's a Python function for sorting...   │
│             │  ```python                                    │
│             │  def sort_list(items):                        │
│  ─────────  │      return sorted(items)                     │
│  📊 Dashboard│  ```                                         │
│             │                          👍 👎  50 tokens     │
│  🔵 Local AI ├───────────────────────────────────────────────┤
│     Active  │  [Ask about code, debugging, best practices...]│
└─────────────┴───────────────────────────────────────────────┘
```

### Module Guide

#### 💬 General Assistant
General purpose AI assistance for everyday questions.

```
Example: "What's the best way to learn machine learning?"
```

#### 👨‍💻 Development Assistant
Code generation, review, debugging, and best practices.

```
Examples:
- "Write a Python function to validate email addresses"
- "Debug this code: [paste code]"
- "Review this function for best practices"
- "Explain how async/await works in JavaScript"
```

#### 📈 Trading Analyst
Technical analysis and market insights.

```
Examples:
- "Analyze AAPL with RSI and MACD"
- "What does the RSI indicator mean?"
- "Get technical analysis for BTC-USD"
```

> ⚠️ **Disclaimer**: Trading analysis is for educational purposes only and does not constitute financial advice.

#### 🔬 Research Engine
Web search and document analysis.

```
Examples:
- "Search for recent developments in quantum computing"
- "Upload a document" (via file upload)
- "What does my uploaded document say about X?"
```

### Feedback System

After each AI response, you can:
- 👍 **Thumbs up** - Mark as helpful
- 👎 **Thumbs down** - Mark as unhelpful (optionally provide correction)

Your feedback helps ARIA learn and improve over time.

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### Chat
```http
POST /api/chat/
Content-Type: application/json

{
  "message": "Your message here",
  "session_id": "optional-session-id",
  "module": "general|developer|trading|research"
}
```

#### Trading Analysis
```http
POST /api/trading/analyze
Content-Type: application/json

{
  "symbol": "AAPL",
  "period": "1mo",
  "indicators": ["sma", "rsi", "macd"]
}
```

#### Research Search
```http
POST /api/research/search
Content-Type: application/json

{
  "query": "Your search query",
  "max_results": 5
}
```

#### Submit Feedback
```http
POST /api/feedback/submit
Content-Type: application/json

{
  "session_id": "session-id",
  "message_id": "message-id",
  "rating": 1,
  "correction": "Optional correction text",
  "module": "general"
}
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | Session secret key | (required) |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://aria:aria_password@localhost:5432/aria_db` |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Default LLM model | `mistral:7b-instruct-q4_K_M` |
| `ENCRYPTION_KEY` | Fernet encryption key | (optional) |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

### Model Configuration

For systems with limited RAM, use quantized models:

```bash
# 4-bit quantized (recommended for 16GB RAM)
ollama pull mistral:7b-instruct-q4_K_M

# Smaller model for lower RAM
ollama pull phi:2.7b
```

---

## 🔐 Security

### Security Features

- **Local-Only AI**: All LLM inference runs locally via Ollama
- **Data Encryption**: Sensitive data encrypted with Fernet
- **Input Sanitization**: All user inputs are sanitized
- **Rate Limiting**: API endpoints are rate-limited
- **Audit Logging**: All operations are logged
- **Sandboxed Execution**: Code is validated before execution

### Best Practices

1. **Change Default Secrets**: Update `SECRET_KEY` and `ENCRYPTION_KEY` in production
2. **Use HTTPS**: Put behind a reverse proxy with SSL in production
3. **Limit Access**: Use firewall rules to restrict access
4. **Regular Updates**: Keep dependencies updated

---

## 🔧 Troubleshooting

### Common Issues

#### Ollama Connection Failed
```
Error: Unable to connect to Ollama
```
**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

#### Out of Memory
```
Error: CUDA out of memory / RAM exhausted
```
**Solution:**
- Use a smaller quantized model
- Reduce `MAX_CONTEXT_TOKENS` in `.env`
- Close other applications

#### Database Connection Failed
```
Error: Connection refused to PostgreSQL
```
**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres
```

#### Frontend Build Failed
```
Error: Module not found
```
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f ollama
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       ARIA Architecture                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │   Frontend  │────▶│   Backend   │────▶│   Ollama    │    │
│  │   (React)   │     │  (FastAPI)  │     │   (LLM)     │    │
│  └─────────────┘     └──────┬──────┘     └─────────────┘    │
│         │                   │                                │
│         │            ┌──────┴──────┐                        │
│         │            │             │                         │
│         │      ┌─────┴─────┐ ┌─────┴─────┐                  │
│         │      │ PostgreSQL│ │  Modules  │                  │
│         │      │ (Storage) │ │           │                  │
│         │      └───────────┘ │ ┌───────┐ │                  │
│         │                    │ │ Dev   │ │                  │
│         │                    │ │Trading│ │                  │
│         └────────────────────┤ │Research│ │                 │
│                              │ └───────┘ │                  │
│                              └───────────┘                  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Project Structure

```
privateagent/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Agent, LLM, Memory
│   │   ├── modules/         # Developer, Trading, Research
│   │   ├── database/        # SQLAlchemy models
│   │   └── utils/           # Encryption, Logging
│   ├── tests/               # Unit tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API service
│   │   └── types/           # TypeScript types
│   └── Dockerfile
├── docker-compose.yml
├── setup.sh
└── README.md
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/gajjarumesh/privateagent/issues) page.

---

<div align="center">

**Built with ❤️ for local-first AI**

</div>