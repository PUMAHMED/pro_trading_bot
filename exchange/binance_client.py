"""
MEXC Pro Trading Bot - Binance Exchange Client
Binance exchange API client
"""

from typing import List, Dict, Any, Optional
import ccxt.async_support as ccxt
from exchanges.base_client import BaseExchangeClient
from config.settings import exchange_config
from utils.logger import get_logger
from utils.cache import cache_manager

logger = get_logger(__name__)

class BinanceClient(BaseExchangeClient):
    """Binance exchange client"""
    
    def __init__(self):
        super().__init__(
            api_key=exchange_config.BINANCE_API_KEY,
            api_secret=exchange_config.BINANCE_API_SECRET,
            exchange_name='Binance'
        )
        
    async def initialize(self):
        """Binance exchange'i başlat"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'rateLimit': 1000 / exchange_config.BINANCE_RATE_LIMIT * 60000,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            await self.exchange.load_markets()
            logger.info(f"✅ Binance bağlantısı kuruldu - {len(self.exchange.markets)} market")
            
        except Exception as e:
            logger.error(f"❌ Binance başlatma hatası: {e}")
            raise
    
    async def get_all_symbols(self, quote_currency: str = 'USDT') -> List[str]:
        """Tüm USDT çiftlerini al"""
        cache_key = f"binance:symbols:{quote_currency}"
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            symbols = []
            for symbol, market in self.exchange.markets.items():
                if (market['quote'] == quote_currency and 
                    market['active'] and 
                    market['spot']):
                    symbols.append(symbol)
            
            await cache_manager.set(cache_key, symbols, ttl=3600)
            logger.info(f"📊 Binance: {len(symbols)} {quote_currency} çifti bulundu")
            return symbols
            
        except Exception as e:
            self._handle_error(e, 'get_all_symbols')
            return []
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Ticker bilgisi al"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume'],
                'quote_volume': ticker['quoteVolume'],
                'high': ticker['high'],
                'low': ticker['low'],
                'open': ticker['open'],
                'close': ticker['close'],
                'change': ticker['percentage'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            self._handle_error(e, f'get_ticker:{symbol}')
            return {}
    
    async def get_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 100) -> List[List]:
        """OHLCV verisi al"""
        cache_key = f"binance:ohlcv:{symbol}:{timeframe}:{limit}"
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached
        
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            await cache_manager.set(cache_key, ohlcv, ttl=60)
            return ohlcv
            
        except Exception as e:
            self._handle_error(e, f'get_ohlcv:{symbol}')
            return []
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Order book al"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit=limit)
            return {
                'bids': orderbook['bids'],
                'asks': orderbook['asks'],
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            self._handle_error(e, f'get_orderbook:{symbol}')
            return {'bids': [], 'asks': [], 'timestamp': None}
    
    async def get_24h_volume(self, symbol: str) -> float:
        """24 saatlik volume al"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return ticker['quoteVolume'] or 0.0
        except Exception as e:
            self._handle_error(e, f'get_24h_volume:{symbol}')
            return 0.0
    
    async def get_futures_symbols(self) -> List[str]:
        """Futures trading çiftlerini al"""
        try:
            futures_exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'options': {'defaultType': 'future'}
            })
            
            await futures_exchange.load_markets()
            symbols = [s for s in futures_exchange.markets.keys() if futures_exchange.markets[s]['active']]
            await futures_exchange.close()
            
            return symbols
            
        except Exception as e:
            logger.error(f"❌ Binance futures symbols hatası: {e}")
            return []
    
    async def get_funding_rate(self, symbol: str) -> Optional[float]:
        """Funding rate al (futures)"""
        try:
            funding = await self.exchange.fetch_funding_rate(symbol)
            return funding.get('fundingRate')
        except Exception as e:
            logger.debug(f"Funding rate alınamadı: {symbol}")
            return None
    
    async def get_kline_data_detailed(self, symbol: str, interval: str, limit: int = 500) -> List[Dict]:
        """Detaylı kline verisi al"""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, interval, limit=limit)
            
            detailed_data = []
            for candle in ohlcv:
                detailed_data.append({
                    'timestamp': candle[0],
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            return detailed_data
            
        except Exception as e:
            self._handle_error(e, f'get_kline_data_detailed:{symbol}')
            return []
