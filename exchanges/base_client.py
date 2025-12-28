"""
MEXC Pro Trading Bot - Base Exchange Client
Temel exchange client sınıfı
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import ccxt.async_support as ccxt
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseExchangeClient(ABC):
    """Temel exchange client abstract sınıfı"""
    
    def __init__(self, exchange_id: str, api_key: str, api_secret: str):
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange = None
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self):
        """Exchange bağlantısını başlat"""
        pass
    
    @abstractmethod
    async def get_all_symbols(self, quote_currency: str = 'USDT') -> List[str]:
        """Tüm trading çiftlerini getir"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Ticker bilgisi getir"""
        pass
    
    @abstractmethod
    async def get_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 100) -> List[List]:
        """OHLCV verisi getir"""
        pass
    
    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Order book getir"""
        pass
    
    async def close(self):
        """Bağlantıyı kapat"""
        if self.exchange:
            await self.exchange.close()
            logger.info(f"✅ {self.exchange_id} bağlantısı kapatıldı")