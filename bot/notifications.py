"""
MEXC Pro Trading Bot - Notification Manager
Bildirim yönetim sistemi - TP/SL bildirimleri eklendi
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pytz
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
    
    def _get_istanbul_time(self) -> str:
        """İstanbul saatini formatlanmış string olarak al"""
        tz = pytz.timezone(bot_config.TIMEZONE)
        return datetime.now(tz).strftime('%H:%M:%S')
    
    async def send_signal_notification(self, signal: Dict[str, Any], formatted_message: str):
        """Sinyal bildirimi gönder"""
        try:
            # Rate limit kontrolü
            if not self._check_rate_limit():
                logger.warning("⚠️ Bildirim rate limit aşıldı, atlanıyor")
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
    
    async def send_tp_notification(
        self, 
        signal: Dict[str, Any], 
        tp_level: str, 
        price: float, 
        profit: float, 
        duration: str
    ):
        """TP bildir"""
        if not self.config.NOTIFY_TP_REACHED:
            return
        
        try:
            time_str = self._get_istanbul_time()
            
            message = f"""
🎉 <b>HEDEF ULAŞILDI!</b>

💎 Coin: {signal['symbol']}
📊 Exchange: {signal['exchange'].value if hasattr(signal['exchange'], 'value') else signal['exchange']}
🎯 {tp_level}: ${price:.8f}
💰 Kar: +{profit:.2f}%

⏱️ Süre: {duration}
🕒 Saat: {time_str} (İST)

🎊 Tebrikler!
"""
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"🎉 TP bildirimi gönderildi: {signal['symbol']} {tp_level}")
            
        except Exception as e:
            logger.error(f"❌ TP bildirim hatası: {e}")
    
    async def send_sl_notification(self, signal: Dict[str, Any]):
        """SL yaklaşıyor bildirimi"""
        if not self.config.NOTIFY_SL_APPROACHING:
            return
        
        try:
            time_str = self._get_istanbul_time()
            
            message = f"""
⚠️ <b>STOP LOSS YAKLAŞIYOR</b>

💎 Coin: {signal['symbol']}
📊 Exchange: {signal['exchange'].value if hasattr(signal['exchange'], 'value') else signal['exchange']}

🛡️ Stop Loss: ${signal['stop_loss']:.8f}
💰 Şu Anki Fiyat: ${signal.get('current_price', 0):.8f}

🕒 Saat: {time_str} (İST)

⚠️ Pozisyonunuzu gözden geçirin!
"""
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"⚠️ SL bildirimi gönderildi: {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ SL bildirim hatası: {e}")
    
    async def send_signal_cancelled(self, signal: Dict[str, Any], reason: str):
        """Sinyal iptal bildirimi - Analiz bozulması"""
        if not self.config.NOTIFY_ANALYSIS_BROKEN:
            return
        
        try:
            time_str = self._get_istanbul_time()
            
            message = f"""
🚫 <b>SİNYAL İPTAL EDİLDİ</b>

💎 Coin: {signal['symbol']}
📊 Exchange: {signal['exchange'].value if hasattr(signal['exchange'], 'value') else signal['exchange']}

❌ İptal Nedeni:
{reason}

🕒 Saat: {time_str} (İST)

⚠️ Bu coin için pozisyon açmayın veya açtıysanız kapatın!
"""
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"🚫 İptal bildirimi gönderildi: {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ İptal bildirimi hatası: {e}")
    
    async def send_signal_updated(
        self, 
        signal: Dict[str, Any], 
        old_target: float, 
        new_target: float,
        reason: str
    ):
        """Sinyal güncelleme bildirimi - Kar beklentisi artışı"""
        if not self.config.NOTIFY_TARGET_UPDATED:
            return
        
        try:
            time_str = self._get_istanbul_time()
            improvement = ((new_target - old_target) / old_target) * 100
            
            message = f"""
📈 <b>SİNYAL GÜNCELLENDİ</b>

💎 Coin: {signal['symbol']}
📊 Exchange: {signal['exchange'].value if hasattr(signal['exchange'], 'value') else signal['exchange']}

🎯 Eski Hedef: ${old_target:.8f}
🎯 Yeni Hedef: ${new_target:.8f}
📈 İyileşme: +{improvement:.2f}%

💡 Güncelleme Nedeni:
{reason}

🕒 Saat: {time_str} (İST)

✅ Kar beklentisi arttı!
"""
            
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"📈 Güncelleme bildirimi gönderildi: {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ Güncelleme bildirimi hatası: {e}")
    
    async def send_update_notification(self, symbol: str, update_type: str, details: str):
        """Genel güncelleme bildirimi"""
        if not self.config.NOTIFY_TARGET_UPDATED:
            return
        
        try:
            time_str = self._get_istanbul_time()
            
            message = f"""
🔄 <b>GÜNCELLEME</b>

💎 Coin: {symbol}
📊 Tip: {update_type}

{details}

🕒 Saat: {time_str} (İST)
"""
            
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
            time_str = self._get_istanbul_time()
            
            message = f"""
💓 <b>Sistem Durumu</b>

⏰ Saat: {time_str} (İST)
📊 Taranan Coin: {stats.get('avg_coins_per_scan', 0)}
📈 Bugünkü Sinyal: {stats.get('total_signals', 0)}
🎯 Başarı Oranı: {stats.get('success_rate', 0):.1f}%

✅ Sistem normal çalışıyor
"""
            
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
            time_str = self._get_istanbul_time()
            
            message = f"❌ <b>HATA</b>\n\n{error_message}\n\n🕒 {time_str} (İST)"
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