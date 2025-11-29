#!/bin/bash

# ARIA - One-Click Setup Script
# This script sets up the entire ARIA system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Banner
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     █████╗ ██████╗ ██╗ █████╗                                ║"
echo "║    ██╔══██╗██╔══██╗██║██╔══██╗                               ║"
echo "║    ███████║██████╔╝██║███████║                               ║"
echo "║    ██╔══██║██╔══██╗██║██╔══██║                               ║"
echo "║    ██║  ██║██║  ██║██║██║  ██║                               ║"
echo "║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝                               ║"
echo "║                                                               ║"
echo "║    Adaptive Research & Intelligence Agent                    ║"
echo "║    100% Local AI - No External API Dependencies              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check RAM
    if command -v free &> /dev/null; then
        total_ram=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$total_ram" -lt 8 ]; then
            print_warning "System has ${total_ram}GB RAM. Recommended: 16GB for optimal performance."
        else
            print_success "RAM: ${total_ram}GB (OK)"
        fi
    fi
    
    # Check disk space
    if command -v df &> /dev/null; then
        available_space=$(df -BG . | awk 'NR==2 {print $4}' | tr -d 'G')
        if [ "$available_space" -lt 20 ]; then
            print_warning "Available disk space: ${available_space}GB. Recommended: 50GB+"
        else
            print_success "Disk space: ${available_space}GB available (OK)"
        fi
    fi
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed."
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed."
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check and install Ollama
install_ollama() {
    print_status "Checking Ollama installation..."
    
    if ! command -v ollama &> /dev/null; then
        print_warning "Ollama is not installed. Installing..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://ollama.com/install.sh | sh
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            print_error "Please install Ollama manually from: https://ollama.com/download"
            exit 1
        else
            print_error "Unsupported OS. Please install Ollama manually from: https://ollama.com/download"
            exit 1
        fi
    fi
    
    print_success "Ollama is installed"
}

# Pull required models
pull_models() {
    print_status "Pulling required LLM models (this may take a while)..."
    
    # Start Ollama service if not running
    if ! pgrep -x "ollama" > /dev/null; then
        print_status "Starting Ollama service..."
        ollama serve &
        sleep 5
    fi
    
    # Pull Mistral 7B (quantized for efficiency)
    print_status "Pulling Mistral 7B (Q4 quantized)..."
    ollama pull mistral:7b-instruct-q4_K_M || {
        print_warning "Could not pull mistral:7b-instruct-q4_K_M, trying mistral..."
        ollama pull mistral
    }
    
    print_success "Models downloaded successfully"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 64)
        
        # Generate encryption key
        ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")
        
        cp .env.example .env
        
        # Update with generated keys
        if [ -n "$SECRET_KEY" ]; then
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env 2>/dev/null || true
        fi
        
        if [ -n "$ENCRYPTION_KEY" ]; then
            sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env 2>/dev/null || true
        fi
        
        print_success "Environment file created: .env"
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Install Python dependencies (for local development)
install_python_deps() {
    print_status "Checking Python dependencies..."
    
    if [ -d "backend" ]; then
        cd backend
        
        if command -v python3 &> /dev/null; then
            if [ ! -d "venv" ]; then
                print_status "Creating Python virtual environment..."
                python3 -m venv venv
            fi
            
            print_status "Installing Python dependencies..."
            source venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
            deactivate
            
            print_success "Python dependencies installed"
        else
            print_warning "Python 3 not found. Skipping local Python setup."
        fi
        
        cd ..
    fi
}

# Install Node.js dependencies (for local development)
install_node_deps() {
    print_status "Checking Node.js dependencies..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        if command -v npm &> /dev/null; then
            print_status "Installing Node.js dependencies..."
            npm install
            print_success "Node.js dependencies installed"
        else
            print_warning "npm not found. Skipping local Node.js setup."
        fi
        
        cd ..
    fi
}

# Start with Docker Compose
start_docker() {
    print_status "Starting ARIA with Docker Compose..."
    
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    
    print_success "ARIA is starting up..."
    echo ""
    echo "Please wait a moment for all services to initialize."
    echo ""
    print_status "Service URLs:"
    echo "  • Frontend:  http://localhost:3000"
    echo "  • Backend:   http://localhost:8000"
    echo "  • API Docs:  http://localhost:8000/docs"
    echo "  • Ollama:    http://localhost:11434"
    echo ""
}

# Main setup function
main() {
    check_requirements
    check_docker
    create_env_file
    
    echo ""
    echo "Choose setup mode:"
    echo "  1) Docker (Recommended) - Run everything in containers"
    echo "  2) Local Development - Install dependencies locally"
    echo "  3) Docker + Local Ollama - Use local Ollama with Docker services"
    echo ""
    read -p "Enter choice [1-3]: " choice
    
    case $choice in
        1)
            start_docker
            ;;
        2)
            install_ollama
            pull_models
            install_python_deps
            install_node_deps
            echo ""
            print_success "Local development environment is ready!"
            echo ""
            echo "To start the backend:"
            echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
            echo ""
            echo "To start the frontend:"
            echo "  cd frontend && npm start"
            ;;
        3)
            install_ollama
            pull_models
            start_docker
            ;;
        *)
            print_error "Invalid choice. Running Docker setup..."
            start_docker
            ;;
    esac
    
    echo ""
    print_success "Setup complete! 🎉"
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  ARIA is ready! Access the UI at http://localhost:3000       ║"
    echo "║                                                               ║"
    echo "║  Key Features:                                                ║"
    echo "║  • 100% Local AI - No external API calls                     ║"
    echo "║  • Development Assistant - Code help & debugging             ║"
    echo "║  • Trading Analyst - Technical analysis (educational)        ║"
    echo "║  • Research Engine - Web search & document RAG               ║"
    echo "║                                                               ║"
    echo "║  Need help? Check the README.md for documentation.           ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Run main function
main
