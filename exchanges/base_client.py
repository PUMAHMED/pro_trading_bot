“””
MEXC Pro Trading Bot - Base Exchange Client
Temel exchange client sınıfı
“””

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import ccxt.async_support as ccxt
from utils.logger import get_logger

logger = get_logger(**name**)

class BaseExchangeClient(ABC):
“”“Tüm exchange client’ları için base class”””

```
def __init__(self, api_key: str, api_secret: str, exchange_name: str):
    self.api_key = api_key
    self.api_secret = api_secret
    self.exchange_name = exchange_name
    self.exchange = None
    
@abstractmethod
async def initialize(self):
    """Exchange'i başlat"""
    pass

@abstractmethod
async def get_all_symbols(self, quote_currency: str = 'USDT') -> List[str]:
    """Tüm trading çiftlerini al"""
    pass

@abstractmethod
async def get_ticker(self, symbol: str) -> Dict[str, Any]:
    """Ticker bilgisi al"""
    pass

@abstractmethod
async def get_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 100) -> List[List]:
    """OHLCV verisi al"""
    pass

@abstractmethod
async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
    """Order book al"""
    pass

@abstractmethod
async def get_24h_volume(self, symbol: str) -> float:
    """24 saatlik volume al"""
    pass

async def close(self):
    """Exchange bağlantısını kapat"""
    if self.exchange:
        await self.exchange.close()
        logger.info(f"✅ {self.exchange_name} bağlantısı kapatıldı")

def _handle_error(self, error: Exception, operation: str):
    """Hata işleme"""
    error_msg = str(error)
    
    if 'rate limit' in error_msg.lower():
        logger.warning(f"⚠️ {self.exchange_name} rate limit: {operation}")
        raise ccxt.RateLimitExceeded(error_msg)
    elif 'timeout' in error_msg.lower():
        logger.warning(f"⚠️ {self.exchange_name} timeout: {operation}")
        raise ccxt.NetworkError(error_msg)
    else:
        logger.error(f"❌ {self.exchange_name} error in {operation}: {error_msg}")
        raise
```
