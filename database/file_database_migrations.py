"""
MEXC Pro Trading Bot - Database Migrations
Database schema güncellemeleri ve migrasyonlar
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from utils.logger import get_logger

logger = get_logger(__name__)

async def run_migrations(session: AsyncSession) -> bool:
    """Tüm migrasyonları çalıştır"""
    try:
        logger.info("🔄 Database migrasyonları çalıştırılıyor...")
        
        # Migration tablosu oluştur
        await create_migration_table(session)
        
        # Versiyonu kontrol et
        current_version = await get_current_version(session)
        logger.info(f"📊 Mevcut database versiyonu: {current_version}")
        
        # Migrasyonları sırayla çalıştır
        migrations = [
            (1, migration_v1),
            (2, migration_v2),
            (3, migration_v3),
        ]
        
        for version, migration_func in migrations:
            if version > current_version:
                logger.info(f"⬆️ Migration v{version} çalıştırılıyor...")
                await migration_func(session)
                await update_version(session, version)
                logger.info(f"✅ Migration v{version} tamamlandı")
        
        logger.info("✅ Tüm migrasyonlar tamamlandı")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration hatası: {e}", exc_info=True)
        return False

async def create_migration_table(session: AsyncSession):
    """Migration takip tablosu oluştur"""
    query = """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    await session.execute(text(query))
    await session.commit()

async def get_current_version(session: AsyncSession) -> int:
    """Mevcut schema versiyonunu al"""
    try:
        result = await session.execute(
            text("SELECT MAX(version) as version FROM schema_version")
        )
        row = result.one_or_none()
        return row.version if row and row.version else 0
    except:
        return 0

async def update_version(session: AsyncSession, version: int):
    """Version'ı güncelle"""
    await session.execute(
        text("INSERT INTO schema_version (version) VALUES (:version)"),
        {"version": version}
    )
    await session.commit()

# ============================================================================
# MIGRATIONS
# ============================================================================

async def migration_v1(session: AsyncSession):
    """
    Migration v1: İlk schema
    - Tüm temel tablolar oluşturulur (models.py'daki Base.metadata.create_all ile)
    """
    # Bu migration'da yapılacak özel bir şey yok
    # Tablolar zaten models.py'dan oluşturuldu
    pass

async def migration_v2(session: AsyncSession):
    """
    Migration v2: Performance optimizasyonu
    - Ek indexler ekle
    """
    queries = [
        # Signal tablosu için composite index
        """
        CREATE INDEX IF NOT EXISTS idx_signal_exchange_status_created 
        ON signals(exchange, status, created_at DESC)
        """,
        
        # Coin info için volume index
        """
        CREATE INDEX IF NOT EXISTS idx_coin_volume 
        ON coin_info(volume_24h DESC) 
        WHERE is_active = TRUE
        """,
        
        # Scan results için timestamp index
        """
        CREATE INDEX IF NOT EXISTS idx_scan_timestamp_passed 
        ON scan_results(timestamp DESC, passed_filters)
        """,
    ]
    
    for query in queries:
        try:
            await session.execute(text(query))
        except Exception as e:
            logger.warning(f"Index oluşturma hatası (muhtemelen zaten var): {e}")
    
    await session.commit()

async def migration_v3(session: AsyncSession):
    """
    Migration v3: Yeni alanlar ekle
    - Gelecekteki özellikler için reserve
    """
    # Örnek: Yeni kolonlar ekle
    queries = [
        # Signals tablosuna sentiment alanı ekle (future feature)
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='signals' AND column_name='sentiment_score'
            ) THEN
                ALTER TABLE signals ADD COLUMN sentiment_score FLOAT DEFAULT 0;
            END IF;
        END $$;
        """,
    ]
    
    for query in queries:
        try:
            await session.execute(text(query))
        except Exception as e:
            logger.warning(f"Column ekleme hatası: {e}")
    
    await session.commit()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def rollback_migration(session: AsyncSession, version: int) -> bool:
    """Migration'ı geri al (dikkatli kullan!)"""
    try:
        logger.warning(f"⚠️ Migration v{version} geri alınıyor...")
        
        # Version'ı sil
        await session.execute(
            text("DELETE FROM schema_version WHERE version = :version"),
            {"version": version}
        )
        await session.commit()
        
        logger.info(f"✅ Migration v{version} geri alındı")
        return True
        
    except Exception as e:
        logger.error(f"❌ Rollback hatası: {e}")
        return False

async def reset_database(session: AsyncSession) -> bool:
    """
    TÜM VERİYİ SİL VE BAŞTAN OLUŞTUR!
    ⚠️ ÇOK TEHLİKELİ - SADECE DEVELOPMENT'TA KULLAN!
    """
    try:
        logger.warning("⚠️⚠️⚠️ DATABASE RESET - TÜM VERİ SİLİNİYOR!")
        
        # Tüm tabloları sil
        from database.models import Base
        
        # PostgreSQL için
        await session.execute(text("DROP SCHEMA public CASCADE"))
        await session.execute(text("CREATE SCHEMA public"))
        
        # Tabloları yeniden oluştur
        from database.connection import engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database reset tamamlandı")
        return True
        
    except Exception as e:
        logger.error(f"❌ Reset hatası: {e}")
        return False