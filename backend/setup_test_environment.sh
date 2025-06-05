#!/bin/bash

# RepoChat Phase 1-3 Test Environment Setup Script
# This script sets up the complete testing environment for RepoChat

set -e  # Exit on any error

echo "🚀 RepoChat Phase 1-3 Test Environment Setup"
echo "============================================="

# Colors for output
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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running from backend directory
if [[ ! -f "requirements.txt" ]]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

# 1. Check Prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git is required but not installed"
    exit 1
fi
print_success "Git found: $(git --version)"

# Check Docker (optional)
if command -v docker &> /dev/null; then
    print_success "Docker found: $(docker --version)"
    DOCKER_AVAILABLE=true
else
    print_warning "Docker not found - you'll need to install Neo4j manually"
    DOCKER_AVAILABLE=false
fi

# 2. Setup Python Environment
print_status "Setting up Python environment..."

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional testing dependencies
print_status "Installing testing dependencies..."
pip install python-dotenv pytest-asyncio neo4j openai

print_success "Python environment setup complete"

# 3. Setup Neo4j Database
print_status "Setting up Neo4j database..."

if [[ "$DOCKER_AVAILABLE" == true ]]; then
    # Check if Neo4j container already exists
    if docker ps -a --format "table {{.Names}}" | grep -q "neo4j-repochat"; then
        print_warning "Neo4j container 'neo4j-repochat' already exists"
        
        # Check if it's running
        if docker ps --format "table {{.Names}}" | grep -q "neo4j-repochat"; then
            print_success "Neo4j container is already running"
        else
            print_status "Starting existing Neo4j container..."
            docker start neo4j-repochat
            sleep 5
            print_success "Neo4j container started"
        fi
    else
        print_status "Creating and starting Neo4j container..."
        
        # Create Neo4j data directories
        mkdir -p $HOME/neo4j/{data,logs,import,plugins}
        
        # Start Neo4j container
        docker run \
            --name neo4j-repochat \
            -p 7474:7474 -p 7687:7687 \
            -d \
            -v $HOME/neo4j/data:/data \
            -v $HOME/neo4j/logs:/logs \
            -v $HOME/neo4j/import:/var/lib/neo4j/import \
            -v $HOME/neo4j/plugins:/plugins \
            --env NEO4J_AUTH=neo4j/repochat123 \
            --env NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.* \
            neo4j:latest
        
        print_status "Waiting for Neo4j to start..."
        sleep 10
        
        # Wait for Neo4j to be ready
        for i in {1..30}; do
            if curl -f -s -u neo4j:repochat123 http://localhost:7474/db/data/ > /dev/null 2>&1; then
                break
            fi
            echo -n "."
            sleep 2
        done
        echo ""
        
        print_success "Neo4j container created and running"
    fi
    
    # Test Neo4j connection
    print_status "Testing Neo4j connection..."
    if curl -f -s -u neo4j:repochat123 http://localhost:7474/db/data/ > /dev/null 2>&1; then
        print_success "Neo4j is accessible at http://localhost:7474"
        print_success "Neo4j credentials: neo4j/repochat123"
    else
        print_error "Failed to connect to Neo4j"
        exit 1
    fi
else
    print_warning "Docker not available. Please install Neo4j manually:"
    print_warning "1. Download from https://neo4j.com/download/"
    print_warning "2. Install and start Neo4j"
    print_warning "3. Set password to 'repochat123' or update .env file"
    print_warning "4. Ensure it's running on bolt://localhost:7687"
fi

# 4. Setup Environment Configuration
print_status "Setting up environment configuration..."

if [[ ! -f ".env" ]]; then
    print_status "Creating .env file from example..."
    cp env_example.txt .env
    print_warning "Please edit .env file and add your OpenAI API key!"
    print_warning "Get your API key from: https://platform.openai.com/api-keys"
else
    print_success ".env file already exists"
fi

# 5. Create necessary directories
print_status "Creating required directories..."
mkdir -p logs temp test_results

# 6. Test Environment Setup
print_status "Testing environment setup..."

# Test Python imports
print_status "Testing Python imports..."
python3 -c "
import sys
sys.path.append('src')
try:
    from teams.data_acquisition.git_operations_module import GitOperationsModule
    from teams.llm_services.llm_gateway_module import LLMGatewayModule
    from orchestrator.orchestrator_agent import OrchestratorAgent
    print('✅ All Python imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Test Neo4j connection
print_status "Testing Neo4j connection..."
python3 -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'repochat123'))
    with driver.session() as session:
        result = session.run('RETURN 1 as test')
        test_value = result.single()['test']
        if test_value == 1:
            print('✅ Neo4j connection successful')
        else:
            print('❌ Neo4j connection failed')
            exit(1)
    driver.close()
except Exception as e:
    print(f'❌ Neo4j connection error: {e}')
    print('Make sure Neo4j is running and accessible')
    exit(1)
"

# Check OpenAI API key (if configured)
print_status "Checking OpenAI configuration..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key.startswith('sk-') and len(api_key) > 20:
    print('✅ OpenAI API key appears to be configured correctly')
elif api_key and api_key == 'sk-your-actual-openai-api-key-here':
    print('⚠️  Please update OPENAI_API_KEY in .env file with your actual API key')
else:
    print('⚠️  OpenAI API key not configured - LLM tests will be skipped')
"

# 7. Print Summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
print_success "Environment setup completed successfully!"
echo ""
echo "📋 Setup Summary:"
echo "  ✅ Python virtual environment: venv/"
echo "  ✅ Required dependencies installed"
if [[ "$DOCKER_AVAILABLE" == true ]]; then
    echo "  ✅ Neo4j database running (Docker)"
else
    echo "  ⚠️  Neo4j needs manual installation"
fi
echo "  ✅ Environment configuration: .env"
echo "  ✅ Required directories created"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Update your .env file with actual values:"
echo "   - Add your OpenAI API key from https://platform.openai.com/api-keys"
echo "   - Update other settings as needed"
echo ""
echo "2. Run comprehensive tests:"
echo "   cd backend"
echo "   source venv/bin/activate  # Activate virtual environment"
echo "   python comprehensive_phase_1_3_manual_test.py"
echo ""
echo "3. Run specific tests:"
echo "   python comprehensive_phase_1_3_manual_test.py --repo-url https://github.com/octocat/Hello-World.git"
echo "   python comprehensive_phase_1_3_manual_test.py --openai-test  # Include LLM tests"
echo ""
echo "4. Access Neo4j Browser: http://localhost:7474"
echo "   Username: neo4j"
echo "   Password: repochat123"
echo ""
echo "📖 For detailed testing instructions, see:"
echo "   PHASE_1_3_TESTING_GUIDE.md"
echo ""
print_success "Happy testing! 🎯" 