#!/bin/bash

# 🚀 RepoChat Frontend Quick Start Script
# =====================================

echo "🚀 RepoChat Frontend - Quick Start Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found! Please run this script from frontend/ directory"
    echo "Run: cd frontend && ./quick_start.sh"
    exit 1
fi

print_status "Found package.json - correct directory!"

# Check Node.js version
echo ""
echo "📋 Checking System Requirements..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js version: $NODE_VERSION"
else
    print_error "Node.js not found! Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

# Check npm version
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_status "npm version: $NPM_VERSION"
else
    print_error "npm not found!"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing Dependencies..."
if npm install; then
    print_status "Dependencies installed successfully!"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Verify dependencies
echo ""
echo "🔍 Verifying Installation..."
if npm list --depth=0 &> /dev/null; then
    print_status "All dependencies verified!"
else
    print_warning "Some dependency issues detected but continuing..."
fi

# Build test
echo ""
echo "🔨 Testing Production Build..."
if npm run build &> /dev/null; then
    print_status "Production build successful!"
    print_info "Build output in dist/ directory"
else
    print_warning "Production build had issues but dev server should work"
fi

# Start dev server
echo ""
echo "🖥️  Starting Development Server..."
print_info "Server will start at: http://localhost:3000"
print_info "Press Ctrl+C to stop the server"
print_info ""
print_status "✨ Setup Complete! Opening browser in 3 seconds..."

# Countdown
for i in 3 2 1; do
    echo -n "$i... "
    sleep 1
done
echo ""

# Try to open browser automatically
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000 &
elif command -v open &> /dev/null; then
    open http://localhost:3000 &
elif command -v start &> /dev/null; then
    start http://localhost:3000 &
fi

print_status "🚀 Starting Vue.js Development Server..."
echo ""
echo "=========================================="
echo "🎯 MANUAL TESTING CHECKLIST:"
echo "=========================================="
echo "1. ✅ Check sidebar with logo & buttons"  
echo "2. ✅ Try example questions in welcome screen"
echo "3. ✅ Type a message and send (Enter or button)"
echo "4. ✅ Verify bot responds intelligently"
echo "5. ✅ Test 'New Chat' and 'Settings' buttons"
echo "6. ✅ Test on mobile by resizing browser"
echo "=========================================="

# Start the dev server
npm run dev 