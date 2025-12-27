"""
MEXC Pro Trading Bot - Coin Scanner
Çoklu exchange coin tarama motoru
"""

import asyncio
from typing import List, Dict, Any, Set
from datetime import datetime
import ccxt

from exchanges.mexc_client import MEXCClient
from exchanges.binance_client import BinanceClient
from config.settings import scanner_config, performance_config
from config.constants import ExchangeName
from database.connection import get_session
from database.operations import CoinOperations, SystemOperations
from utils.logger import get_logger
from utils.cache import cache_manager

logger = get_logger(__name__)

class CoinScanner:
    """Coin tarama motoru - MEXC ve Binance'den coinleri tarar"""
    
    def __init__(self):
        self.mexc_client = None
        self.binance_client = None
        
        self.config = scanner_config
        self.performance_config = performance_config
        
        self.active_symbols: Set[str] = set()
        self.last_update_time = None
        
        self.is_initialized = False
    
    async def initialize(self):
        """Scanner'ı başlat"""
        try:
            logger.info("🔧 Scanner başlatılıyor...")
            
            # Exchange client'ları başlat
            self.mexc_client = MEXCClient()
            self.binance_client = BinanceClient()
            
            await self.mexc_client.initialize()
            await self.binance_client.initialize()
            
            # İlk coin listesini yükle
            await self._load_initial_coin_list()
            
            self.is_initialized = True
            logger.info(f"✅ Scanner başlatıldı - {len(self.active_symbols)} coin tracking")
            
        except Exception as e:
            logger.error(f"❌ Scanner başlatma hatası: {e}", exc_info=True)
            raise
    
    async def scan_all_exchanges(self) -> List[Dict[str, Any]]:
        """Tüm exchange'leri tara"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            scan_start = datetime.now()
            logger.info("🔍 Exchange taraması başladı...")
            
            # Coin listesini güncelle (her 1 saatte bir)
            if self._should_update_coin_list():
                await self._update_coin_list()
            
            # Paralel tarama
            mexc_task = asyncio.create_task(self._scan_exchange(self.mexc_client, ExchangeName.MEXC))
            binance_task = asyncio.create_task(self._scan_exchange(self.binance_client, ExchangeName.BINANCE))
            
            mexc_results, binance_results = await asyncio.gather(
                mexc_task,
                binance_task,
                return_exceptions=True
            )
            
            # Sonuçları birleştir
            all_results = []
            
            if isinstance(mexc_results, list):
                all_results.extend(mexc_results)
            else:
                logger.error(f"❌ MEXC tarama hatası: {mexc_results}")
            
            if isinstance(binance_results, list):
                all_results.extend(binance_results)
            else:
                logger.error(f"❌ Binance tarama hatası: {binance_results}")
            
            # Filtreleme
            filtered_results = await self._apply_filters(all_results)
            
            scan_duration = (datetime.now() - scan_start).total_seconds()
            logger.info(
                f"✅ Tarama tamamlandı: {len(all_results)} coin, "
                f"{len(filtered_results)} passed filters ({scan_duration:.2f}s)"
            )
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ Exchange tarama hatası: {e}", exc_info=True)
            return []
    
    async def _scan_exchange(
        self,
        client: Any,
        exchange_name: ExchangeName
    ) -> List[Dict[str, Any]]:
        """Tek bir exchange'i tara"""
        try:
            # Quote currency'lere göre coinleri al
            all_symbols = []
            for quote in self.config.QUOTE_CURRENCIES:
                symbols = await client.get_all_symbols(quote)
                all_symbols.extend(symbols)
            
            logger.info(f"📊 {exchange_name.value}: {len(all_symbols)} symbol bulundu")
            
            # Paralel batch tarama
            batch_size = self.performance_config.MAX_CONCURRENT_TASKS
            results = []
            
            for i in range(0, len(all_symbols), batch_size):
                batch = all_symbols[i:i + batch_size]
                batch_tasks = [
                    self._scan_symbol(client, symbol, exchange_name)
                    for symbol in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Başarılı sonuçları al
                for result in batch_results:
                    if isinstance(result, dict) and result.get('success'):
                        results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ {exchange_name.value} tarama hatası: {e}")
            return []
    
    async def _scan_symbol(
        self,
        client: Any,
        symbol: str,
        exchange_name: ExchangeName
    ) -> Dict[str, Any]:
        """Tek bir symbol'ü tara"""
        try:
            # Ticker bilgisi al
            ticker = await client.get_ticker(symbol)
            
            if not ticker:
                return {'success': False}
            
            # Temel filtreleme burada yap (hız için)
            volume_24h = ticker.get('quote_volume', 0)
            price = ticker.get('last', 0)
            
            # Min volume ve price kontrolü
            if volume_24h < self.config.MIN_VOLUME_USD:
                return {'success': False, 'reason': 'low_volume'}
            
            if price < self.config.MIN_PRICE or price > self.config.MAX_PRICE:
                return {'success': False, 'reason': 'price_out_of_range'}
            
            # OHLCV verisi al (15m timeframe)
            ohlcv = await client.get_ohlcv(symbol, '15m', limit=100)
            
            if len(ohlcv) < 50:
                return {'success': False, 'reason': 'insufficient_data'}
            
            # Volatilite hesapla
            closes = [candle[4] for candle in ohlcv]
            volatility = self._calculate_volatility(closes)
            
            # Volatilite kontrolü
            if volatility < self.config.MIN_VOLATILITY or volatility > self.config.MAX_VOLATILITY:
                return {'success': False, 'reason': 'volatility_out_of_range'}
            
            # Başarılı tarama
            return {
                'success': True,
                'symbol': symbol,
                'exchange': exchange_name,
                'ticker': ticker,
                'ohlcv': ohlcv,
                'volatility': volatility,
                'volume_24h': volume_24h,
                'price': price,
                'timestamp': datetime.utcnow()
            }
            
        except ccxt.RateLimitExceeded:
            await asyncio.sleep(1)
            return {'success': False, 'reason': 'rate_limit'}
        except Exception as e:
            logger.debug(f"Symbol tarama hatası {symbol}: {str(e)[:100]}")
            return {'success': False, 'reason': 'error'}
    
    async def _apply_filters(self, scan_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ek filtreleme uygula"""
        filtered = []
        
        for result in scan_results:
            if not result.get('success'):
                continue
            
            # Order book al (manipülasyon kontrolü için)
            try:
                exchange_name = result['exchange']
                symbol = result['symbol']
                
                # Client seç
                client = self.mexc_client if exchange_name == ExchangeName.MEXC else self.binance_client
                
                orderbook = await client.get_orderbook(symbol, limit=20)
                result['orderbook'] = orderbook
                
                # Spread kontrolü
                if orderbook and orderbook.get('bids') and orderbook.get('asks'):
                    best_bid = orderbook['bids'][0][0]
                    best_ask = orderbook['asks'][0][0]
                    spread_percent = (best_ask - best_bid) / best_bid * 100
                    
                    from config.settings import manipulation_config
                    if spread_percent > manipulation_config.MAX_SPREAD_PERCENT:
                        continue  # Çok geniş spread
                
                filtered.append(result)
                
            except Exception as e:
                logger.debug(f"Filter hatası {result.get('symbol')}: {e}")
                continue
        
        return filtered
    
    def _calculate_volatility(self, closes: List[float]) -> float:
        """24 saatlik volatilite hesapla"""
        if len(closes) < 2:
            return 0.0
        
        # Son 96 mum (24 saat, 15m timeframe)
        recent_closes = closes[-96:] if len(closes) >= 96 else closes
        
        returns = []
        for i in range(1, len(recent_closes)):
            if recent_closes[i-1] != 0:
                ret = (recent_closes[i] - recent_closes[i-1]) / recent_closes[i-1]
                returns.append(ret)
        
        if not returns:
            return 0.0
        
        import numpy as np
        volatility = np.std(returns) * np.sqrt(96) * 100
        
        return volatility
    
    async def _load_initial_coin_list(self):
        """İlk coin listesini yükle"""
        try:
            # MEXC coinleri
            for quote in self.config.QUOTE_CURRENCIES:
                mexc_symbols = await self.mexc_client.get_all_symbols(quote)
                self.active_symbols.update(mexc_symbols)
            
            # Binance coinleri
            for quote in self.config.QUOTE_CURRENCIES:
                binance_symbols = await self.binance_client.get_all_symbols(quote)
                self.active_symbols.update(binance_symbols)
            
            self.last_update_time = datetime.now()
            
            # Database'e kaydet
            async with get_session() as session:
                for symbol in self.active_symbols:
                    exchange = ExchangeName.MEXC
                    
                    await CoinOperations.upsert_coin(session, {
                        'symbol': symbol,
                        'exchange': exchange,
                        'is_active': True,
                        'last_scanned': datetime.utcnow()
                    })
            
            logger.info(f"📊 {len(self.active_symbols)} coin listesi yüklendi")
            
        except Exception as e:
            logger.error(f"❌ Coin listesi yükleme hatası: {e}")
    
    def _should_update_coin_list(self) -> bool:
        """Coin listesi güncellenmeli mi?"""
        if not self.last_update_time:
            return True
        
        time_diff = (datetime.now() - self.last_update_time).total_seconds()
        return time_diff > 3600
    
    async def _update_coin_list(self):
        """Coin listesini güncelle (yeni coinler için)"""
        try:
            old_count = len(self.active_symbols)
            
            for quote in self.config.QUOTE_CURRENCIES:
                mexc_symbols = await self.mexc_client.get_all_symbols(quote)
                binance_symbols = await self.binance_client.get_all_symbols(quote)
                
                new_symbols = (set(mexc_symbols) | set(binance_symbols)) - self.active_symbols
                
                if new_symbols:
                    logger.info(f"🆕 {len(new_symbols)} yeni coin tespit edildi")
                    self.active_symbols.update(new_symbols)
            
            self.last_update_time = datetime.now()
            new_count = len(self.active_symbols)
            
            if new_count > old_count:
                logger.info(f"📊 Coin listesi güncellendi: {old_count} -> {new_count}")
            
        except Exception as e:
            logger.error(f"❌ Coin listesi güncelleme hatası: {e}")
    
    async def get_symbol_details(self, symbol: str, exchange: ExchangeName) -> Dict[str, Any]:
        """Belirli bir symbol'ün detaylarını al"""
        try:
            client = self.mexc_client if exchange == ExchangeName.MEXC else self.binance_client
            
            ticker = await client.get_ticker(symbol)
            ohlcv = await client.get_ohlcv(symbol, '15m', limit=100)
            orderbook = await client.get_orderbook(symbol)
            
            return {
                'symbol': symbol,
                'exchange': exchange,
                'ticker': ticker,
                'ohlcv': ohlcv,
                'orderbook': orderbook
            }
            
        except Exception as e:
            logger.error(f"❌ Symbol detay hatası {symbol}: {e}")
            return {}
    
    async def close(self):
        """Scanner'ı kapat"""
        if self.mexc_client:
            await self.mexc_client.close()
        if self.binance_client:
            await self.binance_client.close()
        
        logger.info("✅ Scanner kapatıldı")
