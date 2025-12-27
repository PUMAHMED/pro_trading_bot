"""
MEXC Pro Trading Bot - Cache Manager
Caching sistemi
"""

from typing import Any, Optional
from datetime import datetime, timedelta
import json
from cachetools import TTLCache
from config.settings import bot_config, performance_config
from utils.logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    """Cache yönetim sınıfı"""
    
    def __init__(self):
        self.enabled = performance_config.USE_CACHE
        self.ttl = bot_config.CACHE_TTL
        
        # In-memory cache
        self.memory_cache = TTLCache(maxsize=1000, ttl=self.ttl)
        
        # Redis cache (opsiyonel)
        self.redis_client = None
        if bot_config.REDIS_URL:
            try:
                import redis.asyncio as redis
                self.redis_client = redis.from_url(bot_config.REDIS_URL)
                logger.info("✅ Redis cache bağlantısı kuruldu")
            except Exception as e:
                logger.warning(f"⚠️ Redis bağlantısı kurulamadı, in-memory cache kullanılacak: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        if not self.enabled:
            return None
        
        try:
            # Önce memory cache'e bak
            if key in self.memory_cache:
                logger.debug(f"💾 Memory cache hit: {key}")
                return self.memory_cache[key]
            
            # Redis cache'e bak
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug(f"💾 Redis cache hit: {key}")
                    data = json.loads(value)
                    # Memory cache'e de ekle
                    self.memory_cache[key] = data
                    return data
            
            logger.debug(f"❌ Cache miss: {key}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache get hatası: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Cache'e veri kaydet"""
        if not self.enabled:
            return False
        
        try:
            # Memory cache'e kaydet
            self.memory_cache[key] = value
            
            # Redis'e kaydet
            if self.redis_client:
                ttl = ttl or self.ttl
                await self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
            
            logger.debug(f"💾 Cache set: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache set hatası: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Cache'den sil"""
        try:
            # Memory cache'den sil
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Redis'ten sil
            if self.redis_client:
                await self.redis_client.delete(key)
            
            logger.debug(f"🗑️ Cache deleted: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache delete hatası: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Pattern'e uyan tüm cache'leri temizle"""
        count = 0
        
        try:
            # Memory cache'i temizle
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
                count += 1
            
            # Redis'i temizle
            if self.redis_client:
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor=cursor,
                        match=f"*{pattern}*",
                        count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            
            logger.info(f"🗑️ Cache pattern cleared: {pattern} ({count} items)")
            return count
            
        except Exception as e:
            logger.error(f"❌ Cache clear pattern hatası: {e}")
            return count
    
    async def clear_all(self) -> bool:
        """Tüm cache'i temizle"""
        try:
            self.memory_cache.clear()
            
            if self.redis_client:
                await self.redis_client.flushdb()
            
            logger.info("🗑️ Tüm cache temizlendi")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache clear all hatası: {e}")
            return False
    
    async def close(self):
        """Cache bağlantısını kapat"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("✅ Redis bağlantısı kapatıldı")

# Global cache instance
cache_manager = CacheManager()