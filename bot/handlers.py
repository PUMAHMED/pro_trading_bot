"""
MEXC Pro Trading Bot - Bot Handlers
Telegram komut ve callback handler'ları
"""

from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import BotKeyboards
from database.connection import get_session
from database.operations import SignalOperations, SystemOperations
from utils.logger import get_logger

logger = get_logger(__name__)

class BotHandlers:
    """Telegram bot handler'ları"""
    
    def __init__(self, scanner, signal_generator, performance_monitor):
        self.scanner = scanner
        self.signal_generator = signal_generator
        self.performance_monitor = performance_monitor
        self.keyboards = BotKeyboards()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start komutu"""
        welcome_message = """
🤖 <b>MEXC Pro Trading Bot</b>

Hoş geldiniz! Ben profesyonel bir kripto trading sinyal botuyum.

📊 <b>Özellikler:</b>
• MEXC ve Binance'deki tüm coinleri tarama
• Teknik analiz, volume analizi, pattern detection
• Pump/dump ve manipülasyon tespiti
• Akıllı risk yönetimi
• ML destekli tahminleme
• Günlük PDF raporları

🎯 <b>Hedefim:</b>
Size en az %4 kar hedefli, yüksek kaliteli sinyaller sunmak.

Menüden istediğiniz işlemi seçebilirsiniz 👇
"""
        await update.message.reply_text(
            welcome_message,
            parse_mode='HTML',
            reply_markup=self.keyboards.main_menu()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/ help komutu"""
        help_text = """
📚 <b>Komutlar:</b>

/start - Botu başlat
/help - Yardım menüsü
/status - Bot durumu
/stats - İstatistikler
/analyze SYMBOL - Coin analiz et
/report - Günlük rapor

📊 <b>Butonlar:</b>
Ana menüden tüm özelliklere erişebilirsiniz.

⚙️ <b>Ayarlar:</b>
Bildirim tercihleri, filtreler ve risk ayarlarını özelleştirebilirsiniz.
"""
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/ status komutu"""
        stats = self.performance_monitor.get_stats()
        health = self.performance_monitor.get_health_status()
        
        status_message = f"""
{health} <b>Sistem Durumu</b>

⏰ Uptime: {stats['uptime_formatted']}
📊 Toplam Tarama: {stats['total_scans']}
📈 Toplam Sinyal: {stats['total_signals']}
⚡ Ortalama Tarama: {stats['avg_scan_duration']:.2f}s
🎯 Sinyal/Saat: {stats['signals_per_hour']:.1f}

❌ Hatalar: {stats['total_errors']}
"""
        await update.message.reply_text(status_message, parse_mode='HTML')
    
    async def stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """İstatistikler"""
        query = update.callback_query
        await query.answer()
        
        async with get_session() as session:
            stats = await SignalOperations.get_signal_statistics(session, days=1)
        
        stats_message = f"""
📊 <b>Günlük İstatistikler</b>

📈 Toplam Sinyal: {stats['total_signals']}
✅ TP1 Hit: {stats['tp1_hit_count']}
🎯 Başarı Oranı: {stats['success_rate']:.1f}%

💰 Ortalama Kar: {stats['avg_profit']:.2f}%
🏆 Max Kar: {stats['max_profit']:.2f}%
📉 Min Kar: {stats['min_profit']:.2f}%

⏱️ Ortalama Süre: {stats['avg_duration_minutes']:.0f} dakika
"""
        await query.edit_message_text(
            stats_message,
            parse_mode='HTML',
            reply_markup=self.keyboards.back_to_main()
        )
    
    async def analyze_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manuel analiz"""
        query = update.callback_query
        await query.answer()
        
        message = """
🔍 <b>Manuel Coin Analizi</b>

Analiz etmek istediğiniz coin'i şu formatta gönderin:

<code>/analyze SYMBOL</code>

Örnek:
<code>/analyze BTC/USDT</code>
<code>/analyze ETH/USDT</code>
"""
        await query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=self.keyboards.back_to_main()
        )
    
    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ayarlar menüsü"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "⚙️ <b>Ayarlar</b>\n\nNeyi değiştirmek istersiniz?",
            parse_mode='HTML',
            reply_markup=self.keyboards.settings_menu()
        )
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ana menü"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🤖 <b>Ana Menü</b>\n\nİşlem seçin:",
            parse_mode='HTML',
            reply_markup=self.keyboards.main_menu()
        )
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bilinmeyen komut"""
        await update.message.reply_text(
            "❓ Bilinmeyen komut. /help yazarak yardım alabilirsiniz."
        )
