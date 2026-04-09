#!/bin/bash
# Setup script for Web-LLM Agentic System Frontend

echo "🚀 Web-LLM Agentic System - Setup Script"
echo "========================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create .env files if not exist
echo -e "\n${BLUE}Setting up environment files...${NC}"

if [ ! -f "backend/.env" ]; then
    echo "DATABASE_URL=sqlite:///./test.db" > backend/.env
    echo "✓ Created backend/.env"
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "VITE_API_URL=http://localhost:8000" > frontend/.env.local
    echo "✓ Created frontend/.env.local"
fi

# Setup Backend
echo -e "\n${BLUE}Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

echo "Installing Python dependencies..."
pip install -r requirements_full.txt

cd ..

# Setup Frontend
echo -e "\n${BLUE}Setting up Frontend...${NC}"
cd frontend

echo "Installing Node dependencies..."
npm install

cd ..

echo -e "\n${GREEN}✓ Setup complete!${NC}"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  python app/main.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "The application will be available at http://localhost:5173"
echo "API documentation at http://localhost:8000/docs"
