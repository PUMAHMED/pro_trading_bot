"""
MEXC Pro Trading Bot - Telegram Bot
Ana Telegram bot sınıfı
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers import BotHandlers
from bot.notifications import NotificationManager
from config.settings import bot_config
from utils.logger import get_logger

logger = get_logger(__name__)

class TelegramBot:
    """Telegram bot ana sınıfı"""
    
    def __init__(self, scanner, signal_generator, performance_monitor):
        self.token = bot_config.TELEGRAM_TOKEN
        self.admin_id = bot_config.ADMIN_ID
        
        self.scanner = scanner
        self.signal_generator = signal_generator
        self.performance_monitor = performance_monitor
        
        self.app = None
        self.notification_manager = None
        self.handlers = None
        
        self.is_running = False
    
    async def start(self):
        """Bot'u başlat"""
        try:
            logger.info("🤖 Telegram bot başlatılıyor...")
            
            # Application oluştur
            self.app = Application.builder().token(self.token).build()
            
            # Notification manager
            self.notification_manager = NotificationManager(self.app.bot)
            
            # Handlers
            self.handlers = BotHandlers(
                self.scanner,
                self.signal_generator,
                self.performance_monitor
            )
            
            # Komutları ve callback'leri kaydet
            self._register_handlers()
            
            # Bot'u başlat
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            
            self.is_running = True
            logger.info("✅ Telegram bot başlatıldı")
            
            # Admin'e başlangıç mesajı
            await self.app.bot.send_message(
                chat_id=self.admin_id,
                text="✅ Bot başarıyla başlatıldı ve çalışıyor!"
            )
            
        except Exception as e:
            logger.error(f"❌ Bot başlatma hatası: {e}", exc_info=True)
            raise
    
    def _register_handlers(self):
        """Tüm handler'ları kaydet"""
        
        # Komutlar
        self.app.add_handler(CommandHandler("start", self.handlers.start_command))
        self.app.add_handler(CommandHandler("help", self.handlers.help_command))
        self.app.add_handler(CommandHandler("status", self.handlers.status_command))
        self.app.add_handler(CommandHandler("analyze", self.handlers.analyze_command))
        
        # Ana menü callbacks
        self.app.add_handler(CallbackQueryHandler(self.handlers.stats_callback, pattern='^stats$'))
        self.app.add_handler(CallbackQueryHandler(self.handlers.analyze_callback, pattern='^analyze$'))
        self.app.add_handler(CallbackQueryHandler(self.handlers.settings_callback, pattern='^settings$'))
        self.app.add_handler(CallbackQueryHandler(self.handlers.report_callback, pattern='^report$'))
        self.app.add_handler(CallbackQueryHandler(self.handlers.notifications_callback, pattern='^notifications$'))
        self.app.add_handler(CallbackQueryHandler(self.handlers.status_callback, pattern='^status$'))
        self.app.add_handler(CallbackQueryHandler(self.handlers.main_menu_callback, pattern='^main_menu$'))
        
        # Ayarlar callbacks
        self.app.add_handler(CallbackQueryHandler(
            self.handlers.settings_notifications_callback, 
            pattern='^settings_notifications$'
        ))
        self.app.add_handler(CallbackQueryHandler(
            self.handlers.settings_filters_callback, 
            pattern='^settings_filters$'
        ))
        self.app.add_handler(CallbackQueryHandler(
            self.handlers.settings_risk_callback, 
            pattern='^settings_risk$'
        ))
        
        # Unknown commands
        self.app.add_handler(MessageHandler(filters.COMMAND, self.handlers.unknown_command))
        
        logger.info("✅ Tüm handler'lar kaydedildi")
    
    async def send_signal(self, signal: dict):
        """Sinyal gönder"""
        try:
            formatted_message = self.signal_generator.format_signal_message(signal)
            await self.notification_manager.send_signal_notification(signal, formatted_message)
        except Exception as e:
            logger.error(f"❌ Sinyal gönderme hatası: {e}")
    
    async def send_tp_notification(self, signal: dict, tp_level: str, price: float, profit: float, duration: str):
        """TP bildirimi gönder"""
        try:
            await self.notification_manager.send_tp_notification(signal, tp_level, price, profit, duration)
        except Exception as e:
            logger.error(f"❌ TP bildirimi hatası: {e}")
    
    async def send_sl_notification(self, signal: dict):
        """SL bildirimi gönder"""
        try:
            message = f"""
⚠️ <b>STOP LOSS YAKLAŞIYOR</b>

💎 Coin: {signal['symbol']}
📊 Exchange: {signal['exchange'].value}

🛡️ Stop Loss: ${signal['stop_loss']:.8f}
💰 Şu Anki Fiyat: ${signal['current_price']:.8f}

⚠️ Pozisyonunuzu gözden geçirin!
"""
            await self.app.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"❌ SL bildirimi hatası: {e}")
    
    async def send_heartbeat(self, stats: dict):
        """Heartbeat gönder"""
        try:
            await self.notification_manager.send_heartbeat(stats)
        except Exception as e:
            logger.error(f"❌ Heartbeat gönderme hatası: {e}")
    
    async def send_daily_report(self, report_path: str):
        """Günlük rapor gönder"""
        try:
            with open(report_path, 'rb') as f:
                await self.app.bot.send_document(
                    chat_id=self.admin_id,
                    document=f,
                    caption="📄 Günlük Trading Raporu"
                )
        except Exception as e:
            logger.error(f"❌ Rapor gönderme hatası: {e}")
    
    async def stop(self):
        """Bot'u durdur"""
        if self.app and self.is_running:
            logger.info("🛑 Telegram bot durduruluyor...")
            await self.app.stop()
            await self.app.shutdown()
            self.is_running = False
            logger.info("✅ Telegram bot durduruldu")