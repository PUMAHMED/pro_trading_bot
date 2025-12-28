"""
MEXC Pro Trading Bot - Whale Tracker
Balina aktivitesi takip modülü
"""

from typing import Dict, Any, List, Optional
from config.settings import manipulation_config
from utils.logger import get_logger

logger = get_logger(__name__)


class WhaleTracker:
    """Balina order takibi"""
    
    def __init__(self):
        self.config = manipulation_config
        self.whale_threshold = self.config.WHALE_ORDER_THRESHOLD
    
    async def analyze_orderbook(self, orderbook: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Order book'ta balina aktivitesi analiz et"""
        try:
            if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
                return self._empty_analysis()
            
            bids = orderbook['bids']
            asks = orderbook['asks']
            
            # Balina orderları tespit et
            whale_bids = self._find_whale_orders(bids, current_price, 'bid')
            whale_asks = self._find_whale_orders(asks, current_price, 'ask')
            
            # Total order book depth
            total_bid_volume = sum(bid[0] * bid[1] for bid in bids[:20])
            total_ask_volume = sum(ask[0] * ask[1] for ask in asks[:20])
            total_volume = total_bid_volume + total_ask_volume
            
            # Whale dominance
            whale_bid_volume = sum(w['total_usd'] for w in whale_bids)
            whale_ask_volume = sum(w['total_usd'] for w in whale_asks)
            total_whale_volume = whale_bid_volume + whale_ask_volume
            
            whale_dominance = (total_whale_volume / total_volume * 100) if total_volume > 0 else 0
            
            # Pressure direction
            if whale_bid_volume > whale_ask_volume * 1.5:
                pressure_direction = 'bullish'
            elif whale_ask_volume > whale_bid_volume * 1.5:
                pressure_direction = 'bearish'
            else:
                pressure_direction = 'neutral'
            
            # Manipulation risk
            manipulation_risk = self._assess_manipulation_risk(
                whale_dominance,
                len(whale_bids),
                len(whale_asks)
            )
            
            # Suspicious patterns
            is_suspicious = (
                whale_dominance > self.config.MAX_WHALE_DOMINANCE or
                self._detect_spoofing_pattern(whale_bids, whale_asks)
            )
            
            return {
                'has_whale_activity': len(whale_bids) + len(whale_asks) > 0,
                'whale_bids': whale_bids,
                'whale_asks': whale_asks,
                'whale_bid_count': len(whale_bids),
                'whale_ask_count': len(whale_asks),
                'whale_bid_volume_usd': round(whale_bid_volume, 2),
                'whale_ask_volume_usd': round(whale_ask_volume, 2),
                'whale_dominance_percent': round(whale_dominance, 2),
                'pressure_direction': pressure_direction,
                'manipulation_risk': manipulation_risk,
                'is_suspicious': is_suspicious
            }
            
        except Exception as e:
            logger.error(f"❌ Whale analiz hatası: {e}")
            return self._empty_analysis()
    
    def _find_whale_orders(self, orders: List[List], current_price: float, side: str) -> List[Dict[str, Any]]:
        """Balina orderlarını tespit et"""
        whale_orders = []
        
        for order in orders[:20]:
            price = order[0]
            amount = order[1]
            total_usd = price * amount
            
            if total_usd >= self.whale_threshold:
                distance_percent = abs((price - current_price) / current_price * 100)
                
                whale_orders.append({
                    'side': side,
                    'price': round(price, 8),
                    'amount': round(amount, 4),
                    'total_usd': round(total_usd, 2),
                    'distance_percent': round(distance_percent, 2)
                })
        
        return whale_orders
    
    def _assess_manipulation_risk(self, dominance: float, bid_count: int, ask_count: int) -> str:
        """Manipülasyon riskini değerlendir"""
        if dominance > 50:
            return 'extreme'
        elif dominance > 30:
            return 'high'
        elif dominance > 20 or (bid_count > 5 or ask_count > 5):
            return 'medium'
        else:
            return 'low'
    
    def _detect_spoofing_pattern(self, whale_bids: List[Dict], whale_asks: List[Dict]) -> bool:
        """Spoofing pattern tespit et"""
        # Tek tarafta çok fazla büyük order = spoofing şüphesi
        if len(whale_bids) > 3 and len(whale_asks) == 0:
            return True
        if len(whale_asks) > 3 and len(whale_bids) == 0:
            return True
        
        return False
    
    def calculate_order_book_imbalance(self, orderbook: Dict[str, Any]) -> float:
        """Order book imbalance hesapla"""
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if not bids or not asks:
                return 0.0
            
            bid_volume = sum(bid[0] * bid[1] for bid in bids[:10])
            ask_volume = sum(ask[0] * ask[1] for ask in asks[:10])
            
            total_volume = bid_volume + ask_volume
            
            if total_volume == 0:
                return 0.0
            
            imbalance = ((bid_volume - ask_volume) / total_volume) * 100
            
            return imbalance
            
        except Exception as e:
            logger.error(f"❌ Imbalance hesaplama hatası: {e}")
            return 0.0
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz"""
        return {
            'has_whale_activity': False,
            'whale_bids': [],
            'whale_asks': [],
            'whale_bid_count': 0,
            'whale_ask_count': 0,
            'whale_bid_volume_usd': 0,
            'whale_ask_volume_usd': 0,
            'whale_dominance_percent': 0,
            'pressure_direction': 'neutral',
            'manipulation_risk': 'low',
            'is_suspicious': False
        }