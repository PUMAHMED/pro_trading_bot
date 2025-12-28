"""
MEXC Pro Trading Bot - Risk Manager
Risk yönetimi ve position sizing
"""

from typing import Dict, Any, List
from config.settings import trading_config
from utils.logger import get_logger

logger = get_logger(__name__)


class RiskManager:
    """Risk yönetim sınıfı"""
    
    def __init__(self):
        self.config = trading_config
        self.max_correlation = 0.7
        
        logger.info("✅ RiskManager başlatıldı")
    
    async def evaluate_signal(
        self,
        signal: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sinyali risk perspektifinden değerlendir
        Returns: {'approved': bool, 'reason': str, 'adjustments': dict}
        """
        
        reasons = []
        adjustments = {}
        
        # 1. Risk/Reward oranı kontrolü
        rr_ratio = self._calculate_risk_reward(signal)
        if rr_ratio < self.config.MIN_RISK_REWARD:
            return {
                'approved': False,
                'reason': f'Risk/Reward oranı çok düşük: {rr_ratio:.2f}',
                'adjustments': {}
            }
        
        # 2. Stop loss mesafe kontrolü
        sl_percent = abs((signal['stop_loss'] - signal['entry_price']) / signal['entry_price'] * 100)
        if sl_percent > self.config.MAX_STOP_LOSS:
            adjustments['stop_loss_warning'] = f'SL mesafesi yüksek: {sl_percent:.2f}%'
        
        # 3. Kaldıraç kontrolü
        if signal['leverage'] > 100 and signal['score'] < 80:
            adjustments['leverage'] = 100
            adjustments['leverage_reason'] = 'Skor düşük olduğu için kaldıraç düşürüldü'
        
        # 4. Volatilite riski
        manipulation = analysis.get('manipulation_analysis', {})
        if manipulation.get('checks', {}).get('volatility_spike', False):
            return {
                'approved': False,
                'reason': 'Volatilite spike tespit edildi - çok riskli',
                'adjustments': {}
            }
        
        # 5. Likidite kontrolü
        orderbook = analysis.get('orderbook_analysis', {})
        if not orderbook.get('is_liquid', True):
            return {
                'approved': False,
                'reason': 'Yetersiz likidite',
                'adjustments': {}
            }
        
        # 6. Position size hesapla
        position_size = self.calculate_position_size(
            signal['entry_price'],
            signal['stop_loss']
        )
        signal['recommended_position_size'] = position_size
        
        return {
            'approved': True,
            'reason': 'Risk kontrollerinden geçti',
            'adjustments': adjustments,
            'risk_reward_ratio': rr_ratio,
            'position_size': position_size
        }
    
    def _calculate_risk_reward(self, signal: Dict[str, Any]) -> float:
        """Risk/Reward oranını hesapla"""
        entry = signal['entry_price']
        tp1 = signal['tp1']
        sl = signal['stop_loss']
        
        risk = abs(entry - sl)
        reward = abs(tp1 - entry)
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        account_size: float = 1000,
        risk_percent: float = None
    ) -> float:
        """
        Position size hesapla
        Kelly Criterion ve fixed percentage risk kullanarak
        """
        if risk_percent is None:
            risk_percent = self.config.POSITION_SIZE_PERCENT / 10
        
        risk_amount = account_size * (risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        
        return position_size
    
    def calculate_kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Kelly Criterion ile optimal position size
        Kelly % = W - [(1 - W) / R]
        W = win rate, R = avg_win / avg_loss
        """
        if avg_loss == 0:
            return 0
        
        r = avg_win / avg_loss
        kelly = win_rate - ((1 - win_rate) / r)
        
        kelly = max(0, min(0.25, kelly))
        
        return kelly
    
    def assess_portfolio_risk(
        self,
        active_positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Portfolio risk değerlendirmesi"""
        
        if not active_positions:
            return {
                'total_risk': 0,
                'position_count': 0,
                'is_overexposed': False
            }
        
        total_risk = sum(pos.get('risk_amount', 0) for pos in active_positions)
        position_count = len(active_positions)
        
        is_overexposed = (
            position_count > self.config.MAX_OPEN_POSITIONS or
            total_risk > 20
        )
        
        return {
            'total_risk': total_risk,
            'position_count': position_count,
            'is_overexposed': is_overexposed,
            'avg_risk_per_position': total_risk / position_count if position_count > 0 else 0
        }