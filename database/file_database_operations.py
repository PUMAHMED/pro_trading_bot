"""
MEXC Pro Trading Bot - Database Operations
CRUD işlemleri ve veritabanı fonksiyonları
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    Signal, AnalysisSnapshot, CoinInfo, ScanResult,
    WhaleActivity, PerformanceMetric, MLPrediction,
    SystemLog, UserPreference
)
from config.constants import SignalStatus, SignalQuality, ExchangeName
from utils.logger import get_logger

logger = get_logger(__name__)

class SignalOperations:
    """Signal CRUD işlemleri"""
    
    @staticmethod
    async def create_signal(session: AsyncSession, signal_data: Dict[str, Any]) -> Signal:
        """Yeni sinyal oluştur"""
        signal = Signal(**signal_data)
        session.add(signal)
        await session.flush()
        await session.refresh(signal)
        logger.info(f"✅ Sinyal oluşturuldu: {signal.symbol} - {signal.signal_type.value}")
        return signal
    
    @staticmethod
    async def get_signal(session: AsyncSession, signal_id: int) -> Optional[Signal]:
        """Sinyal getir"""
        result = await session.execute(
            select(Signal).where(Signal.id == signal_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_signals(session: AsyncSession) -> List[Signal]:
        """Aktif sinyalleri getir"""
        result = await session.execute(
            select(Signal).where(
                Signal.status == SignalStatus.ACTIVE
            ).order_by(desc(Signal.created_at))
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_signal(session: AsyncSession, signal_id: int, updates: Dict[str, Any]) -> Optional[Signal]:
        """Sinyali güncelle"""
        signal = await SignalOperations.get_signal(session, signal_id)
        if signal:
            for key, value in updates.items():
                setattr(signal, key, value)
            signal.updated_at = datetime.utcnow()
            await session.flush()
            await session.refresh(signal)
            logger.info(f"🔄 Sinyal güncellendi: {signal.symbol}")
        return signal
    
    @staticmethod
    async def close_signal(session: AsyncSession, signal_id: int, status: SignalStatus, profit: float = None) -> Optional[Signal]:
        """Sinyali kapat"""
        signal = await SignalOperations.get_signal(session, signal_id)
        if signal:
            signal.status = status
            signal.closed_at = datetime.utcnow()
            if profit is not None:
                signal.actual_profit_percent = profit
            
            if signal.created_at:
                duration = (datetime.utcnow() - signal.created_at).total_seconds() / 60
                signal.actual_duration_minutes = int(duration)
            
            await session.flush()
            await session.refresh(signal)
            logger.info(f"🏁 Sinyal kapatıldı: {signal.symbol} - {status.value}")
        return signal
    
    @staticmethod
    async def get_signals_by_date_range(
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        quality: Optional[SignalQuality] = None
    ) -> List[Signal]:
        """Tarih aralığına göre sinyalleri getir"""
        query = select(Signal).where(
            and_(
                Signal.created_at >= start_date,
                Signal.created_at <= end_date
            )
        )
        
        if quality:
            query = query.where(Signal.quality == quality)
        
        query = query.order_by(desc(Signal.created_at))
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_signal_statistics(session: AsyncSession, days: int = 1) -> Dict[str, Any]:
        """Sinyal istatistikleri"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        result = await session.execute(
            select(
                func.count(Signal.id).label('total'),
                func.sum(func.cast(Signal.tp1_hit, Integer)).label('tp1_hits'),
                func.sum(func.cast(Signal.tp2_hit, Integer)).label('tp2_hits'),
                func.sum(func.cast(Signal.tp3_hit, Integer)).label('tp3_hits'),
                func.sum(func.cast(Signal.sl_hit, Integer)).label('sl_hits'),
                func.avg(Signal.actual_profit_percent).label('avg_profit'),
                func.max(Signal.actual_profit_percent).label('max_profit'),
                func.min(Signal.actual_profit_percent).label('min_profit'),
                func.avg(Signal.actual_duration_minutes).label('avg_duration')
            ).where(Signal.created_at >= start_date)
        )
        
        row = result.one()
        
        total = row.total or 0
        tp1_hits = row.tp1_hits or 0
        
        return {
            'total_signals': total,
            'tp1_hit_count': tp1_hits,
            'tp2_hit_count': row.tp2_hits or 0,
            'tp3_hit_count': row.tp3_hits or 0,
            'sl_hit_count': row.sl_hits or 0,
            'success_rate': (tp1_hits / total * 100) if total > 0 else 0,
            'avg_profit': round(row.avg_profit or 0, 2),
            'max_profit': round(row.max_profit or 0, 2),
            'min_profit': round(row.min_profit or 0, 2),
            'avg_duration_minutes': round(row.avg_duration or 0, 2)
        }

class CoinOperations:
    """Coin bilgileri CRUD"""
    
    @staticmethod
    async def upsert_coin(session: AsyncSession, coin_data: Dict[str, Any]) -> CoinInfo:
        """Coin ekle veya güncelle"""
        result = await session.execute(
            select(CoinInfo).where(
                and_(
                    CoinInfo.symbol == coin_data['symbol'],
                    CoinInfo.exchange == coin_data['exchange']
                )
            )
        )
        coin = result.scalar_one_or_none()
        
        if coin:
            for key, value in coin_data.items():
                if key not in ['symbol', 'exchange']:
                    setattr(coin, key, value)
        else:
            coin = CoinInfo(**coin_data)
            session.add(coin)
        
        await session.flush()
        await session.refresh(coin)
        return coin
    
    @staticmethod
    async def get_all_active_coins(session: AsyncSession, exchange: Optional[ExchangeName] = None) -> List[CoinInfo]:
        """Aktif coinleri getir"""
        query = select(CoinInfo).where(CoinInfo.is_active == True)
        
        if exchange:
            query = query.where(CoinInfo.exchange == exchange)
        
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_coin_stats(session: AsyncSession, symbol: str, exchange: ExchangeName, stats: Dict[str, Any]):
        """Coin istatistiklerini güncelle"""
        result = await session.execute(
            select(CoinInfo).where(
                and_(
                    CoinInfo.symbol == symbol,
                    CoinInfo.exchange == exchange
                )
            )
        )
        coin = result.scalar_one_or_none()
        
        if coin:
            for key, value in stats.items():
                setattr(coin, key, value)
            await session.flush()

class AnalysisOperations:
    """Analiz işlemleri"""
    
    @staticmethod
    async def create_snapshot(session: AsyncSession, signal_id: int, analysis_data: Dict[str, Any]) -> AnalysisSnapshot:
        """Analiz snapshot oluştur"""
        analysis_data['signal_id'] = signal_id
        snapshot = AnalysisSnapshot(**analysis_data)
        session.add(snapshot)
        await session.flush()
        await session.refresh(snapshot)
        return snapshot
    
    @staticmethod
    async def get_latest_snapshot(session: AsyncSession, signal_id: int) -> Optional[AnalysisSnapshot]:
        """En son snapshot'ı getir"""
        result = await session.execute(
            select(AnalysisSnapshot)
            .where(AnalysisSnapshot.signal_id == signal_id)
            .order_by(desc(AnalysisSnapshot.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def save_scan_result(session: AsyncSession, scan_data: Dict[str, Any]) -> ScanResult:
        """Tarama sonucunu kaydet"""
        scan_result = ScanResult(**scan_data)
        session.add(scan_result)
        await session.flush()
        return scan_result

class PerformanceOperations:
    """Performans metrikleri işlemleri"""
    
    @staticmethod
    async def upsert_daily_metrics(session: AsyncSession, date: datetime, metrics: Dict[str, Any]) -> PerformanceMetric:
        """Günlük metrikleri ekle veya güncelle"""
        date_only = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await session.execute(
            select(PerformanceMetric).where(PerformanceMetric.date == date_only)
        )
        metric = result.scalar_one_or_none()
        
        if metric:
            for key, value in metrics.items():
                setattr(metric, key, value)
        else:
            metrics['date'] = date_only
            metric = PerformanceMetric(**metrics)
            session.add(metric)
        
        await session.flush()
        await session.refresh(metric)
        return metric
    
    @staticmethod
    async def get_metrics_by_date_range(
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> List[PerformanceMetric]:
        """Tarih aralığına göre metrikleri getir"""
        result = await session.execute(
            select(PerformanceMetric)
            .where(
                and_(
                    PerformanceMetric.date >= start_date,
                    PerformanceMetric.date <= end_date
                )
            )
            .order_by(asc(PerformanceMetric.date))
        )
        return result.scalars().all()

class WhaleOperations:
    """Balina aktivitesi işlemleri"""
    
    @staticmethod
    async def record_whale_activity(session: AsyncSession, whale_data: Dict[str, Any]) -> WhaleActivity:
        """Balina aktivitesini kaydet"""
        whale = WhaleActivity(**whale_data)
        session.add(whale)
        await session.flush()
        return whale
    
    @staticmethod
    async def get_recent_whale_activity(
        session: AsyncSession,
        symbol: str,
        hours: int = 24
    ) -> List[WhaleActivity]:
        """Son balina aktivitelerini getir"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = await session.execute(
            select(WhaleActivity)
            .where(
                and_(
                    WhaleActivity.symbol == symbol,
                    WhaleActivity.timestamp >= start_time
                )
            )
            .order_by(desc(WhaleActivity.timestamp))
        )
        return result.scalars().all()

class SystemOperations:
    """Sistem işlemleri"""
    
    @staticmethod
    async def log_event(
        session: AsyncSession,
        level: str,
        category: str,
        message: str,
        details: Dict[str, Any] = None,
        error_type: str = None,
        stack_trace: str = None
    ) -> SystemLog:
        """Sistem eventi kaydet"""
        log = SystemLog(
            level=level,
            category=category,
            message=message,
            details=details,
            error_type=error_type,
            stack_trace=stack_trace
        )
        session.add(log)
        await session.flush()
        return log
    
    @staticmethod
    async def get_user_preferences(session: AsyncSession, user_id: int) -> Optional[UserPreference]:
        """Kullanıcı tercihlerini getir"""
        result = await session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user_preferences(
        session: AsyncSession,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> UserPreference:
        """Kullanıcı tercihlerini güncelle"""
        result = await session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        user_pref = result.scalar_one_or_none()
        
        if user_pref:
            for key, value in preferences.items():
                setattr(user_pref, key, value)
            user_pref.updated_at = datetime.utcnow()
        else:
            preferences['user_id'] = user_id
            user_pref = UserPreference(**preferences)
            session.add(user_pref)
        
        await session.flush()
        await session.refresh(user_pref)
        return user_pref