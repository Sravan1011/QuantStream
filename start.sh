#!/bin/bash

# Trading Analytics Platform - Launcher Script
# This script starts both backend and frontend servers

echo "🚀 Starting Trading Analytics Platform..."
echo ""

# Check if we're in the correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Start backend
echo "📊 Starting Backend (FastAPI)..."
cd backend
if [ ! -d "venv" ]; then
    echo "❌ Error: Backend virtual environment not found. Please run: cd backend && python -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

venv/bin/python run.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Start frontend
echo "🎨 Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "✨ Trading Analytics Platform is running!"
echo ""
echo "📍 Backend API:  http://localhost:8000"
echo "📍 API Docs:     http://localhost:8000/docs"
echo "📍 Frontend:     http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Servers stopped'; exit 0" INT

# Keep script running
wait
