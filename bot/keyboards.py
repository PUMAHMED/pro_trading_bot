"""
MEXC Pro Trading Bot - Telegram Keyboards
Inline keyboard layouts
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.constants import EMOJIS

class BotKeyboards:
    """Telegram inline keyboard'ları"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Ana menü keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJIS['graph']} İstatistikler", callback_data='stats'),
                InlineKeyboardButton(f"{EMOJIS['magnifying_glass']} Manuel Analiz", callback_data='analyze')
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['gear']} Ayarlar", callback_data='settings'),
                InlineKeyboardButton(f"{EMOJIS['document']} Günlük Rapor", callback_data='report')
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['bell']} Bildirimler", callback_data='notifications'),
                InlineKeyboardButton(f"{EMOJIS['info']} Sistem Durumu", callback_data='status')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Ayarlar menüsü"""
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJIS['bell']} Bildirim Ayarları", callback_data='settings_notifications'),
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['target']} Sinyal Filtreleri", callback_data='settings_filters'),
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['shield']} Risk Ayarları", callback_data='settings_risk'),
            ],
            [
                InlineKeyboardButton(f"« Geri", callback_data='main_menu'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def notification_settings() -> InlineKeyboardMarkup:
        """Bildirim ayarları"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Tüm Sinyaller", callback_data='notif_all_on'),
                InlineKeyboardButton("❌ Tüm Sinyaller", callback_data='notif_all_off')
            ],
            [
                InlineKeyboardButton("✅ Sadece Yüksek Kalite", callback_data='notif_high_only_on'),
                InlineKeyboardButton("❌ Sadece Yüksek Kalite", callback_data='notif_high_only_off')
            ],
            [
                InlineKeyboardButton("✅ TP Bildirimleri", callback_data='notif_tp_on'),
                InlineKeyboardButton("❌ TP Bildirimleri", callback_data='notif_tp_off')
            ],
            [
                InlineKeyboardButton("✅ SL Uyarıları", callback_data='notif_sl_on'),
                InlineKeyboardButton("❌ SL Uyarıları", callback_data='notif_sl_off')
            ],
            [
                InlineKeyboardButton(f"« Geri", callback_data='settings'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def signal_filters() -> InlineKeyboardMarkup:
        """Sinyal filtreleri"""
        keyboard = [
            [
                InlineKeyboardButton("Min Skor: 70", callback_data='filter_score_70'),
                InlineKeyboardButton("Min Skor: 80", callback_data='filter_score_80'),
                InlineKeyboardButton("Min Skor: 90", callback_data='filter_score_90')
            ],
            [
                InlineKeyboardButton("MEXC", callback_data='filter_exchange_mexc'),
                InlineKeyboardButton("Binance", callback_data='filter_exchange_binance'),
                InlineKeyboardButton("Her İkisi", callback_data='filter_exchange_both')
            ],
            [
                InlineKeyboardButton("LONG", callback_data='filter_direction_long'),
                InlineKeyboardButton("SHORT", callback_data='filter_direction_short'),
                InlineKeyboardButton("Her İkisi", callback_data='filter_direction_both')
            ],
            [
                InlineKeyboardButton(f"« Geri", callback_data='settings'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def risk_settings() -> InlineKeyboardMarkup:
        """Risk ayarları"""
        keyboard = [
            [
                InlineKeyboardButton("Max 50x", callback_data='risk_lev_50'),
                InlineKeyboardButton("Max 100x", callback_data='risk_lev_100'),
                InlineKeyboardButton("Max 200x", callback_data='risk_lev_200')
            ],
            [
                InlineKeyboardButton("Risk: Düşük", callback_data='risk_tolerance_low'),
                InlineKeyboardButton("Risk: Orta", callback_data='risk_tolerance_medium'),
                InlineKeyboardButton("Risk: Yüksek", callback_data='risk_tolerance_high')
            ],
            [
                InlineKeyboardButton(f"« Geri", callback_data='settings'),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def scanner_controls() -> InlineKeyboardMarkup:
        """Scanner kontrol butonları"""
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJIS['check']} Başlat", callback_data='scanner_start'),
                InlineKeyboardButton(f"{EMOJIS['cross']} Durdur", callback_data='scanner_stop')
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['lightning']} Tek Tarama", callback_data='scanner_once')
            ],
            [
                InlineKeyboardButton(f"« Geri", callback_data='main_menu')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Ana menüye dön butonu"""
        keyboard = [[InlineKeyboardButton(f"« Ana Menü", callback_data='main_menu')]]
        return InlineKeyboardMarkup(keyboard)
