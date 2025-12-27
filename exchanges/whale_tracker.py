"""
MEXC Pro Trading Bot - Whale Tracker
Balina aktivitesi takibi
"""

from typing import List, Dict, Any, Optional
from config.settings import manipulation_config
from utils.logger import get_logger

logger = get_logger(__name__)

class WhaleTracker:
    """Balina order takibi"""
    
    def __init__(self):
        self.whale_threshold = manipulation_config.WHALE_ORDER_THRESHOLD
        self.max_dominance = manipulation_config.MAX_WHALE_DOMINANCE
    
    async def analyze_orderbook(self, orderbook: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Order book'ta balina aktivitesi analiz et"""
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if not bids or not asks:
                return self._empty_analysis()
            
            # Whale orders tespit et
            whale_bids = self._find_whale_orders(bids, current_price, 'bid')
            whale_asks = self._find_whale_orders(asks, current_price, 'ask')
            
            # Order book dominance hesapla
            total_bid_volume = sum(bid[1] * bid[0] for bid in bids)
            total_ask_volume = sum(ask[1] * ask[0] for ask in asks)
            
            whale_bid_volume = sum(order['total_usd'] for order in whale_bids)
            whale_ask_volume = sum(order['total_usd'] for order in whale_asks)
            
            bid_dominance = (whale_bid_volume / total_bid_volume * 100) if total_bid_volume > 0 else 0
            ask_dominance = (whale_ask_volume / total_ask_volume * 100) if total_ask_volume > 0 else 0
            
            # Whale pressure hesapla
            net_whale_pressure = whale_bid_volume - whale_ask_volume
            pressure_direction = 'bullish' if net_whale_pressure > 0 else 'bearish' if net_whale_pressure < 0 else 'neutral'
            
            # Manipülasyon riski
            manipulation_risk = self._assess_manipulation_risk(
                bid_dominance,
                ask_dominance,
                len(whale_bids),
                len(whale_asks)
            )
            
            return {
                'has_whale_activity': len(whale_bids) > 0 or len(whale_asks) > 0,
                'whale_bids': whale_bids,
                'whale_asks': whale_asks,
                'whale_count': len(whale_bids) + len(whale_asks),
                'bid_dominance_percent': round(bid_dominance, 2),
                'ask_dominance_percent': round(ask_dominance, 2),
                'net_whale_pressure_usd': round(net_whale_pressure, 2),
                'pressure_direction': pressure_direction,
                'manipulation_risk': manipulation_risk,
                'is_suspicious': manipulation_risk in ['high', 'extreme']
            }
            
        except Exception as e:
            logger.error(f"❌ Whale analysis hatası: {e}")
            return self._empty_analysis()
    
    def _find_whale_orders(self, orders: List[List], current_price: float, side: str) -> List[Dict[str, Any]]:
        """Whale orders bul"""
        whale_orders = []
        
        for order in orders:
            price = order[0]
            amount = order[1]
            total_usd = price * amount
            
            if total_usd >= self.whale_threshold:
                distance_percent = abs((price - current_price) / current_price * 100)
                
                whale_orders.append({
                    'side': side,
                    'price': price,
                    'amount': amount,
                    'total_usd': total_usd,
                    'distance_from_price_percent': round(distance_percent, 2)
                })
        
        return whale_orders
    
    def _assess_manipulation_risk(
        self,
        bid_dominance: float,
        ask_dominance: float,
        bid_whale_count: int,
        ask_whale_count: int
    ) -> str:
        """Manipülasyon riski değerlendir"""
        max_dominance = max(bid_dominance, ask_dominance)
        
        if max_dominance > self.max_dominance * 1.5:
            return 'extreme'
        elif max_dominance > self.max_dominance:
            return 'high'
        elif max_dominance > self.max_dominance * 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'has_whale_activity': False,
            'whale_bids': [],
            'whale_asks': [],
            'whale_count': 0,
            'bid_dominance_percent': 0,
            'ask_dominance_percent': 0,
            'net_whale_pressure_usd': 0,
            'pressure_direction': 'neutral',
            'manipulation_risk': 'low',
            'is_suspicious': False
        }
    
    async def detect_spoofing(
        self,
        orderbook_snapshots: List[Dict[str, Any]],
        time_window_seconds: int = 60
    ) -> bool:
        """Spoofing (sahte order) tespit et"""
        # Order book'ta büyük orderların hızlıca eklendi çıkarıldığını kontrol et
        # Bu gelişmiş bir feature, şimdilik basit implement
        return False
    
    def calculate_order_book_imbalance(self, orderbook: Dict[str, Any]) -> float:
        """Order book dengesizliği hesapla"""
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if not bids or not asks:
                return 0.0
            
            # İlk 10 seviye
            bid_volume = sum(bid[1] for bid in bids[:10])
            ask_volume = sum(ask[1] for ask in asks[:10])
            
            total_volume = bid_volume + ask_volume
            if total_volume == 0:
                return 0.0
            
            # Pozitif = daha fazla bid (bullish), Negatif = daha fazla ask (bearish)
            imbalance = (bid_volume - ask_volume) / total_volume * 100
            
            return round(imbalance, 2)
            
        except Exception as e:
            logger.error(f"❌ Order book imbalance hatası: {e}")
            return 0.0
