"""
MEXC Pro Trading Bot - Notification Manager
Bildirim yönetim sistemi
"""

from typing import Dict, Any, Optional
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from config.settings import bot_config, notification_config
from config.constants import NOTIFICATION_TEMPLATES
from utils.logger import get_logger

logger = get_logger(__name__)

class NotificationManager:
    """Bildirim yönetimi"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.admin_id = bot_config.ADMIN_ID
        self.config = notification_config
        
        self.notification_count = 0
        self.last_minute_start = datetime.now()
        
    async def send_signal_notification(self, signal: Dict[str, Any], formatted_message: str):
        """Sinyal bildirimi gönder"""
        try:
            # Rate limit kontrolü
            if not self._check_rate_limit():
                logger.warning("⚠️ Bildirim rate limit aşıldı, atlaniyor")
                return
            
            # Kullanıcı tercihlerine göre filtrele
            if not self._should_send_signal(signal):
                return
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=formatted_message,
                parse_mode='HTML'
            )
            
            self.notification_count += 1
            logger.info(f"📤 Sinyal bildirimi gönderildi: {signal['symbol']}")
            
        except TelegramError as e:
            logger.error(f"❌ Telegram bildirim hatası: {e}")
        except Exception as e:
            logger.error(f"❌ Bildirim hatası: {e}")
    
    async def send_tp_notification(self, signal: Dict[str, Any], tp_level: str, price: float, profit: float, duration: str):
        """TP bildir"""
        if not self.config.NOTIFY_TP_REACHED:
            return
        
        try:
            message = NOTIFICATION_TEMPLATES['tp_reached'].format(
                symbol=signal['symbol'],
                tp_level=tp_level,
                price=price,
                profit=profit,
                duration=duration
            )
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"🎉 TP bildirimi gönderildi: {signal['symbol']} {tp_level}")
            
        except Exception as e:
            logger.error(f"❌ TP bildirim hatası: {e}")
    
    async def send_update_notification(self, symbol: str, update_type: str, details: str):
        """Güncelleme bildirimi"""
        if not self.config.NOTIFY_TARGET_UPDATED:
            return
        
        try:
            message = NOTIFICATION_TEMPLATES['update'].format(
                symbol=symbol,
                update_type=update_type,
                details=details
            )
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"❌ Update bildirim hatası: {e}")
    
    async def send_heartbeat(self, stats: Dict[str, Any]):
        """Sistem durumu heartbeat"""
        try:
            message = NOTIFICATION_TEMPLATES['heartbeat'].format(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                coins_scanned=stats.get('avg_coins_per_scan', 0),
                signals_today=stats.get('total_signals', 0),
                success_rate=stats.get('success_rate', 0)
            )
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("💓 Heartbeat gönderildi")
            
        except Exception as e:
            logger.error(f"❌ Heartbeat bildirim hatası: {e}")
    
    async def send_error_notification(self, error_message: str, error_details: Optional[str] = None):
        """Hata bildirimi"""
        if not self.config.NOTIFY_ERRORS:
            return
        
        try:
            message = f"❌ <b>HATA</b>\n\n{error_message}"
            if error_details:
                message += f"\n\n<code>{error_details[:500]}</code>"
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"❌ Error bildirim hatası: {e}")
    
    def _check_rate_limit(self) -> bool:
        """Rate limit kontrolü"""
        now = datetime.now()
        
        # Yeni dakika başladı mı?
        if (now - self.last_minute_start).total_seconds() >= 60:
            self.notification_count = 0
            self.last_minute_start = now
        
        return self.notification_count < self.config.MAX_NOTIFICATIONS_PER_MINUTE
    
    def _should_send_signal(self, signal: Dict[str, Any]) -> bool:
        """Sinyal gönderilmeli mi?"""
        # Tüm sinyaller kapalıysa
        if not self.config.SEND_ALL_SIGNALS and not self.config.SEND_HIGH_QUALITY_ONLY:
            return False
        
        # Sadece yüksek kalite
        if self.config.SEND_HIGH_QUALITY_ONLY:
            from config.constants import SignalQuality
            return signal['quality'] in [SignalQuality.EXCELLENT, SignalQuality.HIGH]
        
        return True