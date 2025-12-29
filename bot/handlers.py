"""
MEXC Pro Trading Bot - Bot Handlers
Telegram komut ve callback handler'ları
"""

from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import BotKeyboards
from database.connection import get_session
from database.operations import SignalOperations, SystemOperations
from config.constants import ExchangeName
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
• MEXC ve Binance'deki tüm USDT coinlerini tarama
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
        """/help komutu"""
        help_text = """
📚 <b>Komutlar:</b>

/start - Botu başlat
/help - Yardım menüsü
/status - Bot durumu
/stats - İstatistikler
/analyze SYMBOL - Coin analiz et (örn: BTC/USDT)
/report - Günlük rapor

📊 <b>Butonlar:</b>
Ana menüden tüm özelliklere erişebilirsiniz.

⚙️ <b>Ayarlar:</b>
Bildirim tercihleri, filtreler ve risk ayarlarını özelleştirebilirsiniz.

💡 <b>İpucu:</b>
Aynı coin için aynı gün içinde sadece bir kez sinyal gönderilir.
Analiz bozulursa veya kar beklentisi artarsa güncelleme mesajı gelir.
"""
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/status komutu"""
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

📊 Günlük Limit: {self.signal_generator.daily_signal_count}/300
"""
        await update.message.reply_text(status_message, parse_mode='HTML')
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/analyze SYMBOL - Manuel coin analizi"""
        try:
            if not context.args or len(context.args) < 1:
                await update.message.reply_text(
                    "❌ Kullanım: /analyze BTC/USDT\n\n"
                    "Örnek: /analyze ETH/USDT"
                )
                return
            
            symbol = context.args[0].upper()
            
            # Symbol formatını düzelt
            if '/' not in symbol:
                if symbol.endswith('USDT'):
                    symbol = symbol[:-4] + '/USDT'
                else:
                    symbol = symbol + '/USDT'
            
            await update.message.reply_text(f"🔍 {symbol} analiz ediliyor...")
            
            # Exchange seç (varsayılan MEXC)
            exchange = ExchangeName.MEXC
            
            # Symbol detaylarını al
            symbol_details = await self.scanner.get_symbol_details(symbol, exchange)
            
            if not symbol_details or not symbol_details.get('ticker'):
                await update.message.reply_text(
                    f"❌ {symbol} bulunamadı. Lütfen geçerli bir USDT paritesi girin."
                )
                return
            
            # Analiz yap
            from core.analyzer import MarketAnalyzer
            analyzer = MarketAnalyzer()
            
            analysis = await analyzer.analyze_comprehensive(
                symbol=symbol,
                ohlcv_data=symbol_details['ohlcv'],
                orderbook=symbol_details['orderbook'],
                ticker=symbol_details['ticker']
            )
            
            # Sonuçları formatla
            score = analysis.get('overall_score', 0)
            direction = analysis.get('signal_direction', 'UNKNOWN')
            tradeable = analysis.get('is_tradeable', False)
            
            summary = "\n".join(analysis.get('analysis_summary', ['Analiz mevcut değil'])[:5])
            
            result_message = f"""
📊 <b>Manuel Analiz: {symbol}</b>

💯 Skor: {score:.1f}/100
📈 Yön: {direction}
✅ Trade Uygun: {'Evet' if tradeable else 'Hayır'}

<b>Analiz Özeti:</b>
{summary}

<b>Teknik Skorlar:</b>
• Teknik: {analysis['scores']['technical']:.1f}
• Volume: {analysis['scores']['volume']:.1f}
• Orderbook: {analysis['scores']['orderbook']:.1f}
• Pattern: {analysis['scores']['pattern']:.1f}
"""
            
            await update.message.reply_text(result_message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"❌ Manuel analiz hatası: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Analiz sırasında hata oluştu: {str(e)[:100]}"
            )
    
    async def stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """İstatistikler butonu"""
        query = update.callback_query
        await query.answer()
        
        try:
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
        except Exception as e:
            logger.error(f"❌ Stats callback hatası: {e}")
            await query.edit_message_text(
                "❌ İstatistikler yüklenirken hata oluştu.",
                reply_markup=self.keyboards.back_to_main()
            )
    
    async def analyze_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manuel analiz butonu"""
        query = update.callback_query
        await query.answer()
        
        message = """
🔍 <b>Manuel Coin Analizi</b>

Analiz etmek istediğiniz coin'i şu formatta gönderin:

<code>/analyze SYMBOL</code>

Örnekler:
<code>/analyze BTC/USDT</code>
<code>/analyze ETH/USDT</code>
<code>/analyze SOLUSDT</code>
"""
        await query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=self.keyboards.back_to_main()
        )
    
    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ayarlar menüsü butonu"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "⚙️ <b>Ayarlar</b>\n\nNeyi değiştirmek istersiniz?",
            parse_mode='HTML',
            reply_markup=self.keyboards.settings_menu()
        )
    
    async def report_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Günlük rapor butonu"""
        query = update.callback_query
        await query.answer("📄 Rapor oluşturuluyor...")
        
        try:
            from reports.pdf_generator import DailyReportGenerator
            generator = DailyReportGenerator()
            
            report_path = await generator.generate_daily_report()
            
            if report_path:
                with open(report_path, 'rb') as f:
                    await query.message.reply_document(
                        document=f,
                        caption="📄 Günlük Trading Raporu"
                    )
            else:
                await query.message.reply_text("❌ Rapor oluşturulamadı.")
                
        except Exception as e:
            logger.error(f"❌ Report callback hatası: {e}")
            await query.message.reply_text("❌ Rapor oluşturulurken hata oluştu.")
    
    async def notifications_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bildirimler butonu"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🔔 <b>Bildirim Ayarları</b>\n\nBildirim tercihlerinizi ayarlayın:",
            parse_mode='HTML',
            reply_markup=self.keyboards.notification_settings()
        )
    
    async def status_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sistem durumu butonu"""
        query = update.callback_query
        await query.answer()
        
        stats = self.performance_monitor.get_stats()
        health = self.performance_monitor.get_health_status()
        
        status_message = f"""
{health} <b>Sistem Durumu</b>

⏰ Çalışma Süresi: {stats['uptime_formatted']}
📊 Toplam Tarama: {stats['total_scans']}
📈 Toplam Sinyal: {stats['total_signals']}
⚡ Ort. Tarama: {stats['avg_scan_duration']:.2f}s

🎯 Saat Başı Sinyal: {stats['signals_per_hour']:.1f}
❌ Hata Sayısı: {stats['total_errors']}

📊 Günlük: {self.signal_generator.daily_signal_count}/300 sinyal
"""
        await query.edit_message_text(
            status_message,
            parse_mode='HTML',
            reply_markup=self.keyboards.back_to_main()
        )
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ana menü butonu"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🤖 <b>Ana Menü</b>\n\nİşlem seçin:",
            parse_mode='HTML',
            reply_markup=self.keyboards.main_menu()
        )
    
    # Ayarlar callbacks
    async def settings_notifications_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bildirim ayarları"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🔔 <b>Bildirim Ayarları</b>\n\nTercihlerinizi seçin:",
            parse_mode='HTML',
            reply_markup=self.keyboards.notification_settings()
        )
    
    async def settings_filters_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sinyal filtreleri"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🎯 <b>Sinyal Filtreleri</b>\n\nFiltre ayarlarınızı seçin:",
            parse_mode='HTML',
            reply_markup=self.keyboards.signal_filters()
        )
    
    async def settings_risk_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Risk ayarları"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🛡️ <b>Risk Ayarları</b>\n\nRisk tercihlerinizi belirleyin:",
            parse_mode='HTML',
            reply_markup=self.keyboards.risk_settings()
        )
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bilinmeyen komut"""
        await update.message.reply_text(
            "❓ Bilinmeyen komut. /help yazarak yardım alabilirsiniz."
        )