#!/usr/bin/env python
"""
Database viewer script - shows all stored data in SQLite database.
Usage: python view_db.py
"""
import sqlite3
import pandas as pd
from datetime import datetime
import os

db_path = "data/trading_data.db"

def view_database():
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Make sure the backend has been run at least once to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    
    print("=" * 70)
    print("📊 TRADING ANALYTICS DATABASE VIEWER")
    print("=" * 70)
    
    # Tick counts
    print("\n📈 TICK DATA SUMMARY:")
    print("-" * 70)
    try:
        ticks_df = pd.read_sql_query("""
            SELECT symbol, 
                   COUNT(*) as total_ticks,
                   MIN(timestamp) as first_tick,
                   MAX(timestamp) as last_tick,
                   ROUND(AVG(price), 2) as avg_price,
                   ROUND(MIN(price), 2) as min_price,
                   ROUND(MAX(price), 2) as max_price
            FROM ticks 
            GROUP BY symbol
        """, conn)
        if len(ticks_df) > 0:
            print(ticks_df.to_string(index=False))
        else:
            print("No tick data yet. Wait for data to accumulate from WebSocket.")
    except Exception as e:
        print(f"Error reading ticks: {e}")
    
    # OHLC counts
    print("\n\n📊 OHLC DATA SUMMARY:")
    print("-" * 70)
    try:
        ohlc_df = pd.read_sql_query("""
            SELECT symbol, timeframe, 
                   COUNT(*) as candles,
                   MIN(timestamp) as first_candle,
                   MAX(timestamp) as last_candle,
                   ROUND(AVG(close), 2) as avg_close
            FROM ohlc 
            GROUP BY symbol, timeframe
            ORDER BY symbol, timeframe
        """, conn)
        if len(ohlc_df) > 0:
            print(ohlc_df.to_string(index=False))
        else:
            print("No OHLC data yet. Wait for resampling to create candles.")
    except Exception as e:
        print(f"Error reading OHLC: {e}")
    
    # Recent ticks
    print("\n\n🔄 RECENT TICKS (Last 10):")
    print("-" * 70)
    try:
        recent_df = pd.read_sql_query("""
            SELECT symbol, timestamp, ROUND(price, 2) as price, ROUND(size, 6) as size
            FROM ticks 
            ORDER BY timestamp DESC 
            LIMIT 10
        """, conn)
        if len(recent_df) > 0:
            print(recent_df.to_string(index=False))
        else:
            print("No ticks yet.")
    except Exception as e:
        print(f"Error reading recent ticks: {e}")
    
    # Recent OHLC
    print("\n\n📉 RECENT OHLC CANDLES (Last 5 per timeframe):")
    print("-" * 70)
    try:
        for timeframe in ['1s', '1m', '5m']:
            ohlc_recent = pd.read_sql_query(f"""
                SELECT symbol, timestamp, 
                       ROUND(open, 2) as open, 
                       ROUND(high, 2) as high, 
                       ROUND(low, 2) as low, 
                       ROUND(close, 2) as close,
                       ROUND(volume, 4) as volume
                FROM ohlc 
                WHERE timeframe = '{timeframe}'
                ORDER BY timestamp DESC 
                LIMIT 5
            """, conn)
            if len(ohlc_recent) > 0:
                print(f"\n{timeframe} Candles:")
                print(ohlc_recent.to_string(index=False))
    except Exception as e:
        print(f"Error reading OHLC candles: {e}")
    
    # Alerts
    print("\n\n🔔 CONFIGURED ALERTS:")
    print("-" * 70)
    try:
        alerts_df = pd.read_sql_query("""
            SELECT id, name, symbol, metric, condition, threshold, 
                   CASE WHEN is_active = 1 THEN 'Active' ELSE 'Inactive' END as status,
                   last_triggered
            FROM alerts
        """, conn)
        if len(alerts_df) > 0:
            print(alerts_df.to_string(index=False))
        else:
            print("No alerts configured yet.")
    except Exception as e:
        print(f"Error reading alerts: {e}")
    
    # Database stats
    print("\n\n💾 DATABASE STATISTICS:")
    print("-" * 70)
    try:
        cursor = conn.cursor()
        
        # Total rows
        cursor.execute("SELECT COUNT(*) FROM ticks")
        total_ticks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ohlc")
        total_ohlc = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts")
        total_alerts = cursor.fetchone()[0]
        
        # Database size
        db_size = os.path.getsize(db_path) / 1024  # KB
        
        print(f"Total Ticks:     {total_ticks:,}")
        print(f"Total OHLC:      {total_ohlc:,}")
        print(f"Total Alerts:    {total_alerts}")
        print(f"Database Size:   {db_size:.2f} KB")
        
    except Exception as e:
        print(f"Error reading database stats: {e}")
    
    conn.close()
    print("\n" + "=" * 70)
    print("✅ Database view complete!")
    print("\nTip: Run this script periodically to see data accumulation.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    view_database()
