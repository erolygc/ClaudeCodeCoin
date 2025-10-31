#!/bin/bash

# ClaudeCodeCoin - Quick Setup Script
# This script helps you set up Phase 1 POC quickly

set -e  # Exit on error

echo "========================================================================"
echo "🚀 ClaudeCodeCoin - Phase 1 POC Setup"
echo "========================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is installed
print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are installed"

# Check if Python 3 is installed
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
print_success "Python $PYTHON_VERSION is installed"

# Check if secrets.env exists
if [ ! -f "config/secrets.env" ]; then
    print_warning "secrets.env not found. Creating from example..."
    cp config/secrets.env.example config/secrets.env
    print_success "secrets.env created. You can edit it later if needed."
else
    print_success "secrets.env already exists"
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs
print_success "Logs directory created"

# Ask user if they want to install Python dependencies
echo ""
read -p "Do you want to install Python dependencies now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing Python dependencies..."

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1

    # Install dependencies
    print_status "Installing dependencies (this may take a few minutes)..."
    pip install -r requirements.txt

    print_success "Python dependencies installed"
    print_warning "Note: ta-lib may fail to install. It requires system binaries."
    print_warning "For Phase 1 POC, ta-lib is not required."
else
    print_warning "Skipping Python dependencies installation"
    print_warning "You can install them later with: pip install -r requirements.txt"
fi

# Ask user if they want to start Docker services
echo ""
read -p "Do you want to start Docker services now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting Docker services..."
    docker-compose up -d

    print_status "Waiting for services to be ready (30 seconds)..."
    sleep 30

    # Check service status
    print_status "Checking service status..."
    docker-compose ps

    print_success "Docker services started"

    # Ask if user wants to load database schema
    echo ""
    read -p "Do you want to load the database schema now? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Loading database schema..."

        # Wait a bit more for TimescaleDB to be fully ready
        sleep 5

        docker exec -i ccc-timescaledb psql -U ccc_user -d ccc_trading < Phase1_DataBackbone/storage/timescaledb_schema.sql

        if [ $? -eq 0 ]; then
            print_success "Database schema loaded successfully"
        else
            print_error "Failed to load database schema"
            print_warning "You can try manually: docker exec -i ccc-timescaledb psql -U ccc_user -d ccc_trading < Phase1_DataBackbone/storage/timescaledb_schema.sql"
        fi
    else
        print_warning "Skipping database schema loading"
        print_warning "Load it later with: docker exec -i ccc-timescaledb psql -U ccc_user -d ccc_trading < Phase1_DataBackbone/storage/timescaledb_schema.sql"
    fi
else
    print_warning "Skipping Docker services startup"
    print_warning "Start them later with: docker-compose up -d"
fi

# Print final instructions
echo ""
echo "========================================================================"
echo "✅ Setup Complete!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Run tests to verify everything is working:"
echo "   ${GREEN}python tests/run_all_tests.py${NC}"
echo ""
echo "2. Start the Binance data collector (in one terminal):"
echo "   ${GREEN}python Phase1_DataBackbone/collectors/binance_collector.py${NC}"
echo ""
echo "3. Start the Kafka consumer (in another terminal):"
echo "   ${GREEN}python Phase1_DataBackbone/kafka/kafka_consumer.py${NC}"
echo ""
echo "4. Open monitoring dashboards:"
echo "   - Kafka UI: ${BLUE}http://localhost:8080${NC}"
echo "   - Grafana: ${BLUE}http://localhost:3000${NC} (admin/admin)"
echo "   - Prometheus: ${BLUE}http://localhost:9090${NC}"
echo ""
echo "5. Check database:"
echo "   ${GREEN}docker exec -it ccc-timescaledb psql -U ccc_user -d ccc_trading${NC}"
echo ""
echo "For detailed instructions, see: ${YELLOW}QUICKSTART.md${NC}"
echo ""
echo "========================================================================"
