"""
MEXC Pro Trading Bot - Database Connection
Veritabanı bağlantı yönetimi
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from config.settings import bot_config, performance_config
from database.models import Base
from utils.logger import get_logger

logger = get_logger(__name__)

# Global engine ve session maker
engine = None
async_session_maker = None

async def init_database():
    """Veritabanını başlat"""
    global engine, async_session_maker
    
    try:
        # Database URL'i hazırla
        db_url = bot_config.DATABASE_URL
        
        # SQLite için async URL'e çevir
        if db_url.startswith('sqlite'):
            db_url = db_url.replace('sqlite://', 'sqlite+aiosqlite://')
            is_sqlite = True
        # PostgreSQL için async URL'e çevir
        elif db_url.startswith('postgresql'):
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
            is_sqlite = False
        else:
            is_sqlite = 'sqlite' in db_url
        
        logger.info(f"📊 Veritabanı bağlantısı kuruluyor...")
        
        # Engine parametrelerini hazırla
engine_params = {
    'echo': False,
    'future': True
}

# SQLite için özel ayarlar (POOL YOK)
if is_sqlite:
    engine_params['connect_args'] = {'check_same_thread': False}
else:
    # PostgreSQL için pool ayarları
    engine_params.update({
        'pool_size': performance_config.CONNECTION_POOL_SIZE,
        'max_overflow': 20,
        'pool_pre_ping': True,
        'pool_recycle': 3600
    })
        
        # Engine oluştur
        engine = create_async_engine(db_url, **engine_params)
        
        # Session maker oluştur
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Tabloları oluştur
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Veritabanı başarıyla başlatıldı")
        
    except Exception as e:
        logger.error(f"❌ Veritabanı başlatma hatası: {e}", exc_info=True)
        raise

async def close_database():
    """Veritabanı bağlantısını kapat"""
    global engine
    
    if engine:
        logger.info("📊 Veritabanı bağlantısı kapatılıyor...")
        await engine.dispose()
        logger.info("✅ Veritabanı bağlantısı kapatıldı")

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Database session context manager"""
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Database session hatası: {e}", exc_info=True)
            raise
        finally:
            await session.close()

async def test_connection() -> bool:
    """Veritabanı bağlantısını test et"""
    try:
        async with get_session() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        logger.info("✅ Veritabanı bağlantısı başarılı")
        return True
    except Exception as e:
        logger.error(f"❌ Veritabanı bağlantı testi başarısız: {e}")
        return False