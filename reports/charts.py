"""
MEXC Pro Trading Bot - Chart Generator
Grafik oluşturma
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Dict
from datetime import datetime
from config.constants import CHART_STYLE
from utils.logger import get_logger

logger = get_logger(__name__)

class ChartGenerator:
    """Grafik oluşturma sınıfı"""
    
    def __init__(self):
        self.style = CHART_STYLE
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def create_performance_chart(self, signals: List[Dict], output_path: str):
        """Performans grafiği oluştur"""
        try:
            fig, ax = plt.subplots(figsize=self.style['figure_size'], dpi=self.style['dpi'])
            
            dates = [s['created_at'] for s in signals]
            profits = [s.get('actual_profit_percent', 0) for s in signals]
            
            ax.plot(dates, profits, marker='o', linestyle='-', linewidth=2)
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Kar (%)')
            ax.set_title('Günlük Sinyal Performansı')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"📊 Performans grafiği oluşturuldu: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Chart oluşturma hatası: {e}")
    
    def create_win_rate_chart(self, stats: Dict, output_path: str):
        """Win rate pie chart"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            labels = ['TP1 Hit', 'TP2 Hit', 'TP3 Hit', 'SL Hit']
            sizes = [
                stats.get('tp1_hit_count', 0),
                stats.get('tp2_hit_count', 0),
                stats.get('tp3_hit_count', 0),
                stats.get('sl_hit_count', 0)
            ]
            colors = ['#4CAF50', '#2196F3', '#9C27B0', '#F44336']
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Sinyal Sonuç Dağılımı')
            
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Win rate chart hatası: {e}")
