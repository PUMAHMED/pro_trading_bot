"""
MEXC Pro Trading Bot - OrderBook Analyzer
Order book analizi
"""

from typing import Dict, Any, List, Tuple
from config.settings import manipulation_config
from exchanges.whale_tracker import WhaleTracker
from utils.logger import get_logger

logger = get_logger(__name__)

class OrderBookAnalyzer:
    """Order book analiz sınıfı"""
    
    def __init__(self):
        self.config = manipulation_config
        self.whale_tracker = WhaleTracker()
    
    async def analyze(self, orderbook: Dict[str, Any], symbol: str, current_price: float) -> Dict[str, Any]:
        """Order book analizi yap"""
        try:
            if not orderbook or not orderbook.get('bids') or not orderbook.get('asks'):
                logger.warning(f"⚠️ {symbol}: Geçersiz order book")
                return self._empty_analysis()
            
            bids = orderbook['bids']
            asks = orderbook['asks']
            
            # Spread analizi
            spread_percent, spread_category = self._analyze_spread(bids, asks, current_price)
            
            # Depth analizi
            bid_depth, ask_depth, depth_imbalance = self._analyze_depth(bids, asks)
            
            # Order book imbalance
            imbalance = self.whale_tracker.calculate_order_book_imbalance(orderbook)
            
            # Whale analizi
            whale_analysis = await self.whale_tracker.analyze_orderbook(orderbook, current_price)
            
            # Liquidity score
            liquidity_score = self._calculate_liquidity_score(
                bid_depth,
                ask_depth,
                spread_percent
            )
            
            # Support/Resistance walls
            support_walls = self._find_walls(bids, 'support', current_price)
            resistance_walls = self._find_walls(asks, 'resistance', current_price)
            
            # Order book quality
            quality_score = self._assess_quality(
                spread_percent,
                bid_depth,
                ask_depth,
                whale_analysis
            )
            
            # Order book pressure
            pressure_direction = self._determine_pressure(
                depth_imbalance,
                imbalance,
                whale_analysis['pressure_direction']
            )
            
            return {
                'symbol': symbol,
                'orderbook_score': round(quality_score, 2),
                
                # Spread
                'spread_percent': round(spread_percent, 4),
                'spread_category': spread_category,
                'is_tight_spread': spread_percent < self.config.MAX_SPREAD_PERCENT,
                
                # Depth
                'bid_depth_usd': round(bid_depth, 2),
                'ask_depth_usd': round(ask_depth, 2),
                'total_depth_usd': round(bid_depth + ask_depth, 2),
                'depth_imbalance': round(depth_imbalance, 2),
                
                # Imbalance
                'orderbook_imbalance': round(imbalance, 2),
                'imbalance_direction': 'bullish' if imbalance > 0 else 'bearish' if imbalance < 0 else 'neutral',
                
                # Liquidity
                'liquidity_score': round(liquidity_score, 2),
                'is_liquid': bid_depth + ask_depth >= self.config.MIN_ORDER_BOOK_DEPTH,
                
                # Walls
                'support_walls': support_walls,
                'resistance_walls': resistance_walls,
                'has_strong_support': len([w for w in support_walls if w['strength'] == 'strong']) > 0,
                'has_strong_resistance': len([w for w in resistance_walls if w['strength'] == 'strong']) > 0,
                
                # Whale
                'whale_activity': whale_analysis,
                'has_whale_manipulation': whale_analysis['is_suspicious'],
                
                # Overall pressure
                'pressure_direction': pressure_direction
            }
            
        except Exception as e:
            logger.error(f"❌ OrderBook analiz hatası {symbol}: {e}", exc_info=True)
            return self._empty_analysis()
    
    def _analyze_spread(self, bids: List[List], asks: List[List], current_price: float) -> Tuple[float, str]:
        """Spread analizi"""
        if not bids or not asks:
            return 100.0, 'very_wide'
        
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        
        spread = best_ask - best_bid
        spread_percent = (spread / current_price) * 100
        
        # Kategorize et
        if spread_percent < 0.1:
            category = 'very_tight'
        elif spread_percent < 0.3:
            category = 'tight'
        elif spread_percent < 0.5:
            category = 'normal'
        elif spread_percent < 1.0:
            category = 'wide'
        else:
            category = 'very_wide'
        
        return spread_percent, category
    
    def _analyze_depth(self, bids: List[List], asks: List[List]) -> Tuple[float, float, float]:
        """Depth analizi (ilk 10 seviye)"""
        # İlk 10 seviyenin toplam USD değeri
        bid_depth = sum(bid[0] * bid[1] for bid in bids[:10])
        ask_depth = sum(ask[0] * ask[1] for ask in asks[:10])
        
        # Depth imbalance
        total_depth = bid_depth + ask_depth
        if total_depth > 0:
            imbalance = ((bid_depth - ask_depth) / total_depth) * 100
        else:
            imbalance = 0
        
        return bid_depth, ask_depth, imbalance
    
    def _calculate_liquidity_score(self, bid_depth: float, ask_depth: float, spread: float) -> float:
        """Likidite skorunu hesapla"""
        score = 50
        
        # Depth contribution
        total_depth = bid_depth + ask_depth
        if total_depth >= 500000:  # $500K+
            score += 30
        elif total_depth >= 200000:  # $200K+
            score += 20
        elif total_depth >= 100000:  # $100K+
            score += 10
        elif total_depth < 50000:  # $50K'dan az
            score -= 30
        
        # Spread contribution
        if spread < 0.1:
            score += 20
        elif spread < 0.3:
            score += 10
        elif spread > 1.0:
            score -= 20
        
        return max(0, min(100, score))
    
    def _find_walls(self, orders: List[List], wall_type: str, current_price: float) -> List[Dict[str, Any]]:
        """Order book duvarlarını bul"""
        walls = []
        
        if not orders:
            return walls
        
        # Ortalama order boyutunu hesapla
        avg_size = sum(order[1] * order[0] for order in orders[:20]) / 20
        
        for order in orders[:20]:  # İlk 20 seviyeyi kontrol et
            price = order[0]
            amount = order[1]
            total_usd = price * amount
            
            # Wall eşiği: ortalama boyutun 3 katı
            if total_usd > avg_size * 3:
                distance_percent = abs((price - current_price) / current_price * 100)
                
                # Strength belirleme
                if total_usd > avg_size * 10:
                    strength = 'very_strong'
                elif total_usd > avg_size * 6:
                    strength = 'strong'
                else:
                    strength = 'moderate'
                
                walls.append({
                    'type': wall_type,
                    'price': round(price, 8),
                    'amount': round(amount, 4),
                    'total_usd': round(total_usd, 2),
                    'distance_percent': round(distance_percent, 2),
                    'strength': strength
                })
        
        # En güçlü 3 duvarı döndür
        walls.sort(key=lambda x: x['total_usd'], reverse=True)
        return walls[:3]
    
    def _assess_quality(
        self,
        spread: float,
        bid_depth: float,
        ask_depth: float,
        whale_analysis: Dict[str, Any]
    ) -> float:
        """Order book kalitesini değerlendir"""
        score = 50
        
        # Spread quality
        if spread < 0.2:
            score += 20
        elif spread > 0.5:
            score -= 20
        
        # Depth quality
        total_depth = bid_depth + ask_depth
        if total_depth >= 300000:
            score += 20
        elif total_depth < 100000:
            score -= 20
        
        # Balance
        if bid_depth > 0 and ask_depth > 0:
            ratio = max(bid_depth, ask_depth) / min(bid_depth, ask_depth)
            if ratio < 2:  # Balanced
                score += 10
            elif ratio > 5:  # Very imbalanced
                score -= 10
        
        # Whale manipulation penalty
        if whale_analysis['manipulation_risk'] == 'extreme':
            score -= 30
        elif whale_analysis['manipulation_risk'] == 'high':
            score -= 20
        elif whale_analysis['manipulation_risk'] == 'medium':
            score -= 10
        
        return max(0, min(100, score))
    
    def _determine_pressure(
        self,
        depth_imbalance: float,
        order_imbalance: float,
        whale_pressure: str
    ) -> str:
        """Genel order book pressure belirleme"""
        # Vote system
        bullish_votes = 0
        bearish_votes = 0
        
        # Depth imbalance
        if depth_imbalance > 10:
            bullish_votes += 1
        elif depth_imbalance < -10:
            bearish_votes += 1
        
        # Order imbalance
        if order_imbalance > 5:
            bullish_votes += 1
        elif order_imbalance < -5:
            bearish_votes += 1
        
        # Whale pressure
        if whale_pressure == 'bullish':
            bullish_votes += 2  # Whale daha ağırlıklı
        elif whale_pressure == 'bearish':
            bearish_votes += 2
        
        if bullish_votes > bearish_votes + 1:
            return 'strong_bullish'
        elif bullish_votes > bearish_votes:
            return 'bullish'
        elif bearish_votes > bullish_votes + 1:
            return 'strong_bearish'
        elif bearish_votes > bullish_votes:
            return 'bearish'
        else:
            return 'neutral'
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Boş analiz sonucu"""
        return {
            'symbol': '',
            'orderbook_score': 0,
            'spread_percent': 100,
            'spread_category': 'unknown',
            'is_tight_spread': False,
            'bid_depth_usd': 0,
            'ask_depth_usd': 0,
            'total_depth_usd': 0,
            'depth_imbalance': 0,
            'orderbook_imbalance': 0,
            'imbalance_direction': 'neutral',
            'liquidity_score': 0,
            'is_liquid': False,
            'support_walls': [],
            'resistance_walls': [],
            'has_strong_support': False,
            'has_strong_resistance': False,
            'whale_activity': {
                'has_whale_activity': False,
                'manipulation_risk': 'low',
                'is_suspicious': False
            },
            'has_whale_manipulation': False,
            'pressure_direction': 'neutral'
        }