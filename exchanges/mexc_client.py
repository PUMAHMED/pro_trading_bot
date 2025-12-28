"""
MEXC Pro Trading Bot - MEXC Client
MEXC exchange API client
"""

import ccxt.async_support as ccxt
from typing import Dict, Any, List, Optional
from exchanges.base_client import BaseExchangeClient
from config.settings import exchange_config
from config.exchanges import MEXC_CONFIG
from utils.logger import get_logger
from utils.cache import cache_manager

logger = get_logger(__name__)


class MEXCClient(BaseExchangeClient):
    """MEXC exchange client"""
    
    def __init__(self):
        super().__init__(
            exchange_id='mexc',
            api_key=exchange_config.MEXC_API_KEY,
            api_secret=exchange_config.MEXC_API_SECRET
        )
        self.config = MEXC_CONFIG
    
    async def initialize(self):
        """MEXC bağlantısını başlat"""
        try:
            self.exchange = ccxt.mexc({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'rateLimit': 1000 / self.config['rate_limit_per_second'],
                'options': {
                    'defaultType': 'spot'
                }
            })
            
            await self.exchange.load_markets()
            self.is_initialized = True
            logger.info("✅ MEXC bağlantısı başarılı")
            
        except Exception as e:
            logger.error(f"❌ MEXC bağlantı hatası: {e}")
            raise
    
    async def get_all_symbols(self, quote_currency: str = 'USDT') -> List[str]:
        """Tüm USDT çiftlerini getir"""
        try:
            cache_key = f"mexc_symbols_{quote_currency}"
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached
            
            markets = await self.exchange.fetch_markets()
            
            symbols = [
                market['symbol']
                for market in markets
                if market['quote'] == quote_currency
                and market['active']
                and market['spot']
            ]
            
            await cache_manager.set(cache_key, symbols, ttl=3600)
            
            return symbols
            
        except Exception as e:
            logger.error(f"❌ MEXC symbol listesi hatası: {e}")
            return []
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Ticker bilgisi"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            
            return {
                'symbol': symbol,
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
                'volume': ticker.get('baseVolume'),
                'quote_volume': ticker.get('quoteVolume'),
                'change': ticker.get('change'),
                'percentage': ticker.get('percentage'),
                'timestamp': ticker.get('timestamp')
            }
            
        except Exception as e:
            logger.debug(f"Ticker hatası {symbol}: {e}")
            return {}
    
    async def get_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 100) -> List[List]:
        """OHLCV verisi"""
        try:
            cache_key = f"mexc_ohlcv_{symbol}_{timeframe}_{limit}"
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached
            
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            await cache_manager.set(cache_key, ohlcv, ttl=60)
            
            return ohlcv
            
        except Exception as e:
            logger.debug(f"OHLCV hatası {symbol}: {e}")
            return []
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Order book"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit=limit)
            
            return {
                'symbol': symbol,
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp'),
                'datetime': orderbook.get('datetime')
            }
            
        except Exception as e:
            logger.debug(f"Order book hatası {symbol}: {e}")
            return {}
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Son işlemler"""
        try:
            trades = await self.exchange.fetch_trades(symbol, limit=limit)
            return trades
            
        except Exception as e:
            logger.debug(f"Trades hatası {symbol}: {e}")
            return []