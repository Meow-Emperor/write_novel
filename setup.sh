#!/bin/bash
set -e

echo "=== AI Novel Platform Setup ==="
echo ""

# Backend setup
echo "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Initialize database
echo "Initializing database..."
python init_db.py

echo ""
echo "Backend setup complete!"
echo ""

# Frontend setup
cd ../frontend

echo "Setting up frontend..."
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo ""
echo "Frontend setup complete!"
echo ""

cd ..

echo "=== Setup Complete ==="
echo ""
echo "To run the application:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose: docker compose up -d"
echo ""
