"""
MEXC Pro Trading Bot - Statistics Calculator
İstatistik hesaplama modülü
"""

import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from utils.logger import get_logger

logger = get_logger(__name__)


class StatisticsCalculator:
    """İstatistik hesaplayıcı sınıf"""
    
    def __init__(self):
        logger.info("✅ StatisticsCalculator başlatıldı")
    
    async def calculate_daily_statistics(self, signals: List) -> Dict[str, Any]:
        """Günlük istatistikleri hesapla"""
        try:
            if not signals:
                return self._empty_statistics()
            
            total_signals = len(signals)
            
            # TP hit sayıları
            tp1_count = sum(1 for s in signals if s.tp1_hit)
            tp2_count = sum(1 for s in signals if s.tp2_hit)
            tp3_count = sum(1 for s in signals if s.tp3_hit)
            sl_count = sum(1 for s in signals if s.sl_hit)
            
            # Kar/zarar hesaplamaları
            profits = [s.actual_profit_percent for s in signals if s.actual_profit_percent is not None]
            
            avg_profit = np.mean(profits) if profits else 0
            max_profit = max(profits) if profits else 0
            min_profit = min(profits) if profits else 0
            total_profit = sum(profits) if profits else 0
            
            # Süre hesaplamaları
            durations = [s.actual_duration_minutes for s in signals if s.actual_duration_minutes is not None]
            avg_duration = np.mean(durations) if durations else 0
            
            # Başarı oranı
            successful_signals = tp1_count + tp2_count + tp3_count
            success_rate = (successful_signals / total_signals * 100) if total_signals > 0 else 0
            
            # Kalite dağılımı
            quality_distribution = self._calculate_quality_distribution(signals)
            
            # Exchange breakdown
            exchange_breakdown = self._calculate_exchange_breakdown(signals)
            
            # Yön breakdown
            direction_breakdown = self._calculate_direction_breakdown(signals)
            
            # Top coins
            top_coins = self._calculate_top_coins(signals, limit=10)
            
            # Risk/Reward analizi
            risk_reward_analysis = self._calculate_risk_reward_analysis(signals)
            
            # Saatlik dağılım
            hourly_distribution = self._calculate_hourly_distribution(signals)
            
            return {
                'total_signals': total_signals,
                'tp1_count': tp1_count,
                'tp2_count': tp2_count,
                'tp3_count': tp3_count,
                'sl_count': sl_count,
                'successful_signals': successful_signals,
                'overall_success_rate': round(success_rate, 2),
                
                'avg_profit': round(avg_profit, 2),
                'max_profit': round(max_profit, 2),
                'min_profit': round(min_profit, 2),
                'total_profit': round(total_profit, 2),
                
                'avg_duration': round(avg_duration, 2),
                
                'quality_distribution': quality_distribution,
                'exchange_breakdown': exchange_breakdown,
                'direction_breakdown': direction_breakdown,
                'top_coins': top_coins,
                'risk_reward_analysis': risk_reward_analysis,
                'hourly_distribution': hourly_distribution
            }
            
        except Exception as e:
            logger.error(f"❌ İstatistik hesaplama hatası: {e}", exc_info=True)
            return self._empty_statistics()
    
    def _calculate_quality_distribution(self, signals: List) -> Dict[str, int]:
        """Kalite dağılımını hesapla"""
        distribution = defaultdict(int)
        
        for signal in signals:
            quality_str = signal.quality.value
            distribution[quality_str] += 1
        
        return dict(distribution)
    
    def _calculate_exchange_breakdown(self, signals: List) -> Dict[str, Dict[str, Any]]:
        """Exchange breakdown"""
        breakdown = defaultdict(lambda: {
            'count': 0,
            'successful': 0,
            'total_profit': 0
        })
        
        for signal in signals:
            exchange = signal.exchange.value
            breakdown[exchange]['count'] += 1
            
            if signal.tp1_hit or signal.tp2_hit or signal.tp3_hit:
                breakdown[exchange]['successful'] += 1
            
            if signal.actual_profit_percent:
                breakdown[exchange]['total_profit'] += signal.actual_profit_percent
        
        # Success rate hesapla
        for exchange, data in breakdown.items():
            if data['count'] > 0:
                data['success_rate'] = round(data['successful'] / data['count'] * 100, 2)
                data['avg_profit'] = round(data['total_profit'] / data['count'], 2)
        
        return dict(breakdown)
    
    def _calculate_direction_breakdown(self, signals: List) -> Dict[str, Dict[str, Any]]:
        """Yön breakdown"""
        breakdown = defaultdict(lambda: {
            'count': 0,
            'successful': 0,
            'total_profit': 0
        })
        
        for signal in signals:
            direction = signal.signal_type.value
            breakdown[direction]['count'] += 1
            
            if signal.tp1_hit or signal.tp2_hit or signal.tp3_hit:
                breakdown[direction]['successful'] += 1
            
            if signal.actual_profit_percent:
                breakdown[direction]['total_profit'] += signal.actual_profit_percent
        
        # Success rate hesapla
        for direction, data in breakdown.items():
            if data['count'] > 0:
                data['success_rate'] = round(data['successful'] / data['count'] * 100, 2)
                data['avg_profit'] = round(data['total_profit'] / data['count'], 2)
        
        return dict(breakdown)
    
    def _calculate_top_coins(self, signals: List, limit: int = 10) -> List[Dict[str, Any]]:
        """En iyi performans gösteren coinler"""
        coin_profits = defaultdict(list)
        
        for signal in signals:
            if signal.actual_profit_percent is not None:
                coin_profits[signal.symbol].append(signal.actual_profit_percent)
        
        # Her coin için ortalama kar hesapla
        coin_avg_profits = []
        for symbol, profits in coin_profits.items():
            avg_profit = np.mean(profits)
            coin_avg_profits.append({
                'symbol': symbol,
                'profit': round(avg_profit, 2),
                'count': len(profits)
            })
        
        # Kara göre sırala
        coin_avg_profits.sort(key=lambda x: x['profit'], reverse=True)
        
        return coin_avg_profits[:limit]
    
    def _calculate_risk_reward_analysis(self, signals: List) -> Dict[str, Any]:
        """Risk/Reward analizi"""
        risk_rewards = []
        
        for signal in signals:
            entry = signal.entry_price
            tp1 = signal.tp1
            sl = signal.stop_loss
            
            risk = abs(entry - sl)
            reward = abs(tp1 - entry)
            
            if risk > 0:
                rr_ratio = reward / risk
                risk_rewards.append(rr_ratio)
        
        if not risk_rewards:
            return {
                'avg_rr': 0,
                'min_rr': 0,
                'max_rr': 0
            }
        
        return {
            'avg_rr': round(np.mean(risk_rewards), 2),
            'min_rr': round(min(risk_rewards), 2),
            'max_rr': round(max(risk_rewards), 2)
        }
    
    def _calculate_hourly_distribution(self, signals: List) -> Dict[int, int]:
        """Saatlik sinyal dağılımı"""
        hourly_counts = defaultdict(int)
        
        for signal in signals:
            hour = signal.created_at.hour
            hourly_counts[hour] += 1
        
        return dict(hourly_counts)
    
    async def calculate_weekly_statistics(self, signals: List) -> Dict[str, Any]:
        """Haftalık istatistikler"""
        # Günlük istatistiklere ek olarak haftalık trend analizi
        daily_stats = await self.calculate_daily_statistics(signals)
        
        # Günlere göre grupla
        daily_groups = defaultdict(list)
        for signal in signals:
            day = signal.created_at.date()
            daily_groups[day].append(signal)
        
        # Her gün için kar hesapla
        daily_profits = []
        for day, day_signals in sorted(daily_groups.items()):
            profits = [s.actual_profit_percent for s in day_signals if s.actual_profit_percent is not None]
            if profits:
                daily_profits.append({
                    'date': day,
                    'profit': sum(profits),
                    'count': len(day_signals)
                })
        
        daily_stats['daily_breakdown'] = daily_profits
        
        return daily_stats
    
    async def calculate_monthly_statistics(self, signals: List) -> Dict[str, Any]:
        """Aylık istatistikler"""
        daily_stats = await self.calculate_daily_statistics(signals)
        
        # Haftalara göre grupla
        weekly_groups = defaultdict(list)
        for signal in signals:
            week = signal.created_at.isocalendar()[1]
            weekly_groups[week].append(signal)
        
        # Her hafta için kar hesapla
        weekly_profits = []
        for week, week_signals in sorted(weekly_groups.items()):
            profits = [s.actual_profit_percent for s in week_signals if s.actual_profit_percent is not None]
            if profits:
                weekly_profits.append({
                    'week': week,
                    'profit': sum(profits),
                    'count': len(week_signals)
                })
        
        daily_stats['weekly_breakdown'] = weekly_profits
        
        return daily_stats
    
    def calculate_performance_metrics(self, signals: List) -> Dict[str, Any]:
        """Detaylı performans metrikleri"""
        if not signals:
            return {}
        
        # Sharpe Ratio benzeri metrik
        profits = [s.actual_profit_percent for s in signals if s.actual_profit_percent is not None]
        
        if not profits:
            return {}
        
        avg_profit = np.mean(profits)
        std_profit = np.std(profits)
        
        sharpe_like = avg_profit / std_profit if std_profit > 0 else 0
        
        # Win rate by quality
        quality_performance = defaultdict(lambda: {'wins': 0, 'total': 0})
        
        for signal in signals:
            quality = signal.quality.value
            quality_performance[quality]['total'] += 1
            
            if signal.tp1_hit or signal.tp2_hit or signal.tp3_hit:
                quality_performance[quality]['wins'] += 1
        
        # Win rate hesapla
        for quality, data in quality_performance.items():
            if data['total'] > 0:
                data['win_rate'] = round(data['wins'] / data['total'] * 100, 2)
        
        return {
            'sharpe_like_ratio': round(sharpe_like, 2),
            'profit_std': round(std_profit, 2),
            'quality_performance': dict(quality_performance),
            'consistency_score': self._calculate_consistency_score(profits)
        }
    
    def _calculate_consistency_score(self, profits: List[float]) -> float:
        """Tutarlılık skoru (0-100)"""
        if not profits or len(profits) < 2:
            return 0
        
        # Profit'lerin pozitif olma oranı
        positive_ratio = sum(1 for p in profits if p > 0) / len(profits)
        
        # Volatilite (düşük volatilite = daha tutarlı)
        volatility = np.std(profits) / (abs(np.mean(profits)) + 0.0001)
        volatility_score = max(0, 1 - (volatility / 10))
        
        # Combine
        consistency = (positive_ratio * 0.6 + volatility_score * 0.4) * 100
        
        return round(consistency, 2)
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Boş istatistik objesi"""
        return {
            'total_signals': 0,
            'tp1_count': 0,
            'tp2_count': 0,
            'tp3_count': 0,
            'sl_count': 0,
            'successful_signals': 0,
            'overall_success_rate': 0,
            'avg_profit': 0,
            'max_profit': 0,
            'min_profit': 0,
            'total_profit': 0,
            'avg_duration': 0,
            'quality_distribution': {},
            'exchange_breakdown': {},
            'direction_breakdown': {},
            'top_coins': [],
            'risk_reward_analysis': {},
            'hourly_distribution': {}
        }