#!/bin/bash

echo "=== Starting AI Novel Platform (Development Mode) ==="
echo ""

# Check if backend venv exists
if [ ! -d "backend/venv" ]; then
    echo "Error: Backend virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Error: Frontend dependencies not installed!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Start backend in background
echo "Starting backend server..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Start frontend in background
echo "Starting frontend server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
cd ..

echo ""
echo "=== Services Started ==="
echo "Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or create stop script:"
echo "  echo '#!/bin/bash' > stop.sh"
echo "  echo 'kill $BACKEND_PID $FRONTEND_PID' >> stop.sh"
echo "  chmod +x stop.sh"
echo ""

# Create stop script
cat > stop.sh << EOF
#!/bin/bash
echo "Stopping AI Novel Platform..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "Services stopped."
EOF
chmod +x stop.sh

echo "Stop script created: ./stop.sh"
