"""
MEXC Pro Trading Bot - Main Entry Point
Ana çalışma dosyası
"""

import asyncio
import signal
import sys
from datetime import datetime

from config.settings import validate_config, bot_config
from database.connection import init_database, close_database
from core.scanner import CoinScanner
from core.analyzer import MarketAnalyzer
from core.signal_generator import SignalGenerator
from bot.telegram_bot import TelegramBot
from reports.pdf_generator import DailyReportGenerator
from utils.logger import setup_logger, get_logger
from utils.performance import PerformanceMonitor

logger = get_logger(__name__)

class TradingBotApplication:
    """Ana uygulama sınıfı"""
    
    def __init__(self):
        self.scanner = None
        self.analyzer = None
        self.signal_generator = None
        self.telegram_bot = None
        self.report_generator = None
        self.performance_monitor = None
        self.running = False
        
    async def initialize(self):
        """Sistemi başlat"""
        logger.info("🚀 MEXC Pro Trading Bot başlatılıyor...")
        
        # Config doğrulama
        if not validate_config():
            logger.error("❌ Konfigürasyon hatası! Lütfen .env dosyasını kontrol edin.")
            sys.exit(1)
        
        # Database başlat
        logger.info("📊 Veritabanı bağlantısı kuruluyor...")
        await init_database()
        
        # Performans monitörü
        self.performance_monitor = PerformanceMonitor()
        
        # Core components
        logger.info("🔧 Core bileşenler başlatılıyor...")
        self.scanner = CoinScanner()
        self.analyzer = MarketAnalyzer()
        self.signal_generator = SignalGenerator(self.analyzer)
        
        # Telegram bot
        logger.info("🤖 Telegram bot başlatılıyor...")
        self.telegram_bot = TelegramBot(
            scanner=self.scanner,
            signal_generator=self.signal_generator,
            performance_monitor=self.performance_monitor
        )
        
        # Report generator
        self.report_generator = DailyReportGenerator()
        
        logger.info("✅ Tüm bileşenler başarıyla başlatıldı!")
        
    async def start(self):
        """Ana loop'u başlat"""
        self.running = True
        
        # Telegram bot'u başlat
        bot_task = asyncio.create_task(self.telegram_bot.start())
        
        # Ana tarama loop'u
        scan_task = asyncio.create_task(self.main_loop())
        
        # Günlük rapor task'ı
        report_task = asyncio.create_task(self.report_schedule())
        
        # Heartbeat task
        heartbeat_task = asyncio.create_task(self.heartbeat())
        
        # Tüm task'ları çalıştır
        await asyncio.gather(
            bot_task,
            scan_task,
            report_task,
            heartbeat_task,
            return_exceptions=True
        )
    
    async def main_loop(self):
        """Ana tarama döngüsü"""
        logger.info("🔍 Ana tarama döngüsü başladı")
        
        while self.running:
            try:
                start_time = datetime.now()
                
                # Coinleri tara
                scan_results = await self.scanner.scan_all_exchanges()
                
                # Sinyal üret
                signals = await self.signal_generator.process_scan_results(scan_results)
                
                # Sinyalleri gönder
                for signal in signals:
                    await self.telegram_bot.send_signal(signal)
                
                # Performans kaydet
                duration = (datetime.now() - start_time).total_seconds()
                self.performance_monitor.record_scan(duration, len(scan_results), len(signals))
                
                # Bekleme
                from config.settings import scanner_config
                await asyncio.sleep(scanner_config.SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"❌ Ana loop hatası: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def report_schedule(self):
        """Günlük rapor zamanlayıcı"""
        from config.settings import report_config
        import pytz
        
        while self.running:
            try:
                now = datetime.now(pytz.UTC)
                target_hour, target_minute = map(int, report_config.DAILY_REPORT_TIME.split(':'))
                
                target_time = now.replace(
                    hour=target_hour,
                    minute=target_minute,
                    second=0,
                    microsecond=0
                )
                
                if now >= target_time:
                    from datetime import timedelta
                    target_time += timedelta(days=1)
                
                wait_seconds = (target_time - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                logger.info("📄 Günlük rapor oluşturuluyor...")
                report_path = await self.report_generator.generate_daily_report()
                await self.telegram_bot.send_daily_report(report_path)
                
            except Exception as e:
                logger.error(f"❌ Rapor zamanlama hatası: {e}", exc_info=True)
                await asyncio.sleep(3600)
    
    async def heartbeat(self):
        """Sistem sağlık kontrol heartbeat"""
        from config.settings import notification_config
        
        while self.running:
            try:
                await asyncio.sleep(notification_config.HEARTBEAT_INTERVAL)
                
                stats = self.performance_monitor.get_stats()
                await self.telegram_bot.send_heartbeat(stats)
                
            except Exception as e:
                logger.error(f"❌ Heartbeat hatası: {e}", exc_info=True)
    
    async def shutdown(self):
        """Sistemi kapat"""
        logger.info("🛑 Sistem kapatılıyor...")
        self.running = False
        
        if self.telegram_bot:
            await self.telegram_bot.stop()
        
        await close_database()
        
        logger.info("✅ Sistem başarıyla kapatıldı")

app = None

def signal_handler(signum, frame):
    """Signal handler for graceful shutdown"""
    logger.info(f"📡 Signal alındı: {signum}")
    if app:
        asyncio.create_task(app.shutdown())

async def main():
    """Ana fonksiyon"""
    global app
    
    setup_logger()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        app = TradingBotApplication()
        await app.initialize()
        await app.start()
        
    except KeyboardInterrupt:
        logger.info("⌨️ KeyboardInterrupt alındı")
    except Exception as e:
        logger.error(f"❌ Fatal hata: {e}", exc_info=True)
    finally:
        if app:
            await app.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass