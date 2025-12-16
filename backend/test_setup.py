#!/usr/bin/env python
"""
Quick test script to verify backend setup.
"""
import sys
import asyncio

async def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI")
        
        import uvicorn
        print("✓ Uvicorn")
        
        import websockets
        print("✓ WebSockets")
        
        import pandas
        print("✓ Pandas")
        
        import numpy
        print("✓ NumPy")
        
        import scipy
        print("✓ SciPy")
        
        import statsmodels
        print("✓ Statsmodels")
        
        import sklearn
        print("✓ Scikit-learn")
        
        import sqlalchemy
        print("✓ SQLAlchemy")
        
        from app.storage.database import db
        print("✓ Database module")
        
        from app.ingestion.binance_ws import BinanceWebSocketClient
        print("✓ WebSocket client")
        
        from app.analytics import basic_stats, pairs_trading, statistical_tests
        print("✓ Analytics modules")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False


async def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from app.storage.database import db
        await db.init_db()
        print("✓ Database initialized")
        
        # Test insert
        test_tick = {
            'symbol': 'test',
            'timestamp': asyncio.get_event_loop().time(),
            'price': 100.0,
            'size': 1.0
        }
        
        print("✅ Database test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Backend Setup Verification")
    print("=" * 50)
    
    results = []
    
    # Test imports
    results.append(await test_imports())
    
    # Test database
    results.append(await test_database())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ All tests passed! Backend is ready.")
        print("\nTo start the server, run:")
        print("  python run.py")
        print("\nAPI docs will be available at:")
        print("  http://localhost:8000/docs")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
