#!/bin/bash
set -e

# Default values
VITE_API_BASE_URL=${VITE_API_BASE_URL:-"http://localhost:8000"}

echo "🚀 Starting RepoChat Frontend..."
echo "📡 API Base URL: $VITE_API_BASE_URL"

# Create runtime config file for environment variables
cat > /usr/share/nginx/html/config.js << EOF
window.ENV = {
  VITE_API_BASE_URL: '$VITE_API_BASE_URL'
};
EOF

echo "✅ Environment variables configured"

# Start the main command
exec "$@" 