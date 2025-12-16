"""
Alert engine for evaluating and triggering user-defined alerts.
"""
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from app.storage.database import db
from app.storage.redis_client import cache
from app.analytics import basic_stats, pairs_trading

logger = logging.getLogger(__name__)


class AlertEngine:
    """Evaluates alerts and triggers notifications."""
    
    def __init__(self):
        self.running = False
        self.evaluation_task: Optional[asyncio.Task] = None
        self.triggered_alerts: List[Dict[str, Any]] = []
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate if a condition is met."""
        if condition == '>':
            return value > threshold
        elif condition == '<':
            return value < threshold
        elif condition == '>=':
            return value >= threshold
        elif condition == '<=':
            return value <= threshold
        elif condition == '==':
            return abs(value - threshold) < 0.0001
        else:
            return False
    
    async def _evaluate_alert(self, alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate a single alert.
        
        Returns alert trigger data if triggered, None otherwise.
        """
        try:
            symbol = alert['symbol']
            metric = alert['metric']
            condition = alert['condition']
            threshold = alert['threshold']
            
            value = None
            
            # Get metric value based on type
            if metric == 'price':
                # Get latest price from cache or database
                recent_ticks = await cache.get_recent_ticks(symbol, count=1)
                if recent_ticks:
                    value = recent_ticks[-1]['price']
            
            elif metric == 'z_score':
                # Need to parse symbol pair (e.g., "btcusdt_ethusdt")
                if '_' in symbol:
                    symbol1, symbol2 = symbol.split('_', 1)
                    result = await pairs_trading.compute_spread_and_zscore(
                        symbol1, symbol2, timeframe='1m'
                    )
                    if 'current_zscore' in result:
                        value = result['current_zscore']
            
            elif metric == 'volume':
                stats = await basic_stats.compute_basic_stats(symbol, timeframe='1m')
                if 'current_volume' in stats:
                    value = stats['current_volume']
            
            elif metric == 'volatility':
                vol = await basic_stats.compute_volatility(symbol, timeframe='1m')
                if 'rolling_volatility' in vol:
                    value = vol['rolling_volatility']
            
            # Evaluate condition
            if value is not None and self._evaluate_condition(value, condition, threshold):
                return {
                    'alert_id': alert['id'],
                    'alert_name': alert['name'],
                    'symbol': symbol,
                    'metric': metric,
                    'value': value,
                    'condition': condition,
                    'threshold': threshold,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error evaluating alert {alert.get('id')}: {e}")
            return None
    
    async def _evaluation_loop(self):
        """Periodically evaluate all active alerts."""
        while self.running:
            try:
                # Get all active alerts
                alerts = await db.get_alerts(active_only=True)
                
                for alert in alerts:
                    trigger = await self._evaluate_alert(alert)
                    
                    if trigger:
                        # Alert triggered
                        logger.info(f"Alert triggered: {trigger['alert_name']}")
                        
                        # Update last triggered time
                        await db.update_alert_trigger(alert['id'])
                        
                        # Add to triggered alerts list
                        self.triggered_alerts.append(trigger)
                        
                        # Keep only last 100 triggered alerts
                        if len(self.triggered_alerts) > 100:
                            self.triggered_alerts = self.triggered_alerts[-100:]
                
                # Sleep before next evaluation
                await asyncio.sleep(5)  # Evaluate every 5 seconds
            
            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(5)
    
    async def start(self):
        """Start alert evaluation."""
        if self.running:
            return
        
        self.running = True
        self.evaluation_task = asyncio.create_task(self._evaluation_loop())
        logger.info("Alert engine started")
    
    async def stop(self):
        """Stop alert evaluation."""
        if not self.running:
            return
        
        self.running = False
        if self.evaluation_task:
            self.evaluation_task.cancel()
            try:
                await self.evaluation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Alert engine stopped")
    
    def get_recent_triggers(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently triggered alerts."""
        return self.triggered_alerts[-limit:]


# Global alert engine instance
alert_engine = AlertEngine()
