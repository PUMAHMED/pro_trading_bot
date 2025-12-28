"""
MEXC Pro Trading Bot - Chart Generator
Grafik oluşturma modülü
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config.constants import CHART_STYLE
from utils.logger import get_logger

logger = get_logger(__name__)


class ChartGenerator:
    """Grafik oluşturucu sınıf"""
    
    def __init__(self):
        self.style = CHART_STYLE
        self._apply_style()
        logger.info("✅ ChartGenerator başlatıldı")
    
    def _apply_style(self):
        """Matplotlib stil ayarları"""
        try:
            plt.style.use(self.style['style'])
        except:
            plt.style.use('default')
        
        plt.rcParams['figure.figsize'] = self.style['figure_size']
        plt.rcParams['figure.dpi'] = self.style['dpi']
        plt.rcParams['font.size'] = self.style['label_fontsize']
        plt.rcParams['axes.labelsize'] = self.style['label_fontsize']
        plt.rcParams['axes.titlesize'] = self.style['title_fontsize']
        plt.rcParams['xtick.labelsize'] = self.style['tick_fontsize']
        plt.rcParams['ytick.labelsize'] = self.style['tick_fontsize']
        plt.rcParams['legend.fontsize'] = self.style['legend_fontsize']
        plt.rcParams['grid.alpha'] = self.style['grid_alpha']
        plt.rcParams['lines.linewidth'] = self.style['line_width']
    
    def create_performance_chart(
        self,
        dates: List[datetime],
        profits: List[float],
        output_path: str
    ) -> str:
        """Performans grafiği oluştur"""
        try:
            fig, ax = plt.subplots(figsize=self.style['figure_size'])
            
            colors = [self.style['colors']['profit'] if p >= 0 else self.style['colors']['loss'] for p in profits]
            
            ax.bar(dates, profits, color=colors, **self.style['chart_types']['bar'])
            
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Kar/Zarar (%)')
            ax.set_title('Günlük Performans', fontsize=self.style['title_fontsize'])
            ax.grid(True, alpha=self.style['grid_alpha'])
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.style['dpi'], bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Performans grafiği oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Performans grafiği oluşturma hatası: {e}")
            plt.close()
            return ""
    
    def create_win_rate_chart(
        self,
        labels: List[str],
        values: List[float],
        output_path: str
    ) -> str:
        """Win rate grafiği oluştur"""
        try:
            fig, ax = plt.subplots(figsize=(8, 8))
            
            colors = [
                self.style['colors']['success'],
                self.style['colors']['warning'],
                self.style['colors']['danger']
            ]
            
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            
            ax.set_title('Sinyal Başarı Oranları', fontsize=self.style['title_fontsize'])
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.style['dpi'], bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Win rate grafiği oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Win rate grafiği oluşturma hatası: {e}")
            plt.close()
            return ""
    
    def create_signal_distribution_chart(
        self,
        quality_counts: Dict[str, int],
        output_path: str
    ) -> str:
        """Sinyal dağılım grafiği"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            labels = list(quality_counts.keys())
            values = list(quality_counts.values())
            
            colors = [
                self.style['colors']['success'],
                self.style['colors']['primary'],
                self.style['colors']['warning'],
                self.style['colors']['neutral']
            ]
            
            bars = ax.bar(labels, values, color=colors[:len(labels)], **self.style['chart_types']['bar'])
            
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height,
                    f'{int(height)}',
                    ha='center',
                    va='bottom'
                )
            
            ax.set_xlabel('Sinyal Kalitesi')
            ax.set_ylabel('Adet')
            ax.set_title('Sinyal Kalite Dağılımı', fontsize=self.style['title_fontsize'])
            ax.grid(True, alpha=self.style['grid_alpha'], axis='y')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.style['dpi'], bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Dağılım grafiği oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Dağılım grafiği oluşturma hatası: {e}")
            plt.close()
            return ""
    
    def create_cumulative_profit_chart(
        self,
        dates: List[datetime],
        cumulative_profits: List[float],
        output_path: str
    ) -> str:
        """Kümülatif kar grafiği"""
        try:
            fig, ax = plt.subplots(figsize=self.style['figure_size'])
            
            color = self.style['colors']['profit'] if cumulative_profits[-1] >= 0 else self.style['colors']['loss']
            
            ax.plot(dates, cumulative_profits, color=color, **self.style['chart_types']['line'])
            ax.fill_between(dates, cumulative_profits, alpha=self.style['chart_types']['area']['alpha'], color=color)
            
            ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Kümülatif Kar/Zarar (%)')
            ax.set_title('Kümülatif Performans', fontsize=self.style['title_fontsize'])
            ax.grid(True, alpha=self.style['grid_alpha'])
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.style['dpi'], bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Kümülatif kar grafiği oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Kümülatif kar grafiği oluşturma hatası: {e}")
            plt.close()
            return ""
    
    def create_top_coins_chart(
        self,
        coins: List[str],
        profits: List[float],
        output_path: str,
        top_n: int = 10
    ) -> str:
        """En iyi coinler grafiği"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Sort ve top N al
            sorted_data = sorted(zip(coins, profits), key=lambda x: x[1], reverse=True)[:top_n]
            coins_sorted, profits_sorted = zip(*sorted_data) if sorted_data else ([], [])
            
            colors = [self.style['colors']['profit'] if p >= 0 else self.style['colors']['loss'] for p in profits_sorted]
            
            bars = ax.barh(coins_sorted, profits_sorted, color=colors, **self.style['chart_types']['bar'])
            
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(
                    width,
                    bar.get_y() + bar.get_height()/2.,
                    f'{profits_sorted[i]:.2f}%',
                    ha='left' if width >= 0 else 'right',
                    va='center',
                    fontsize=self.style['tick_fontsize']
                )
            
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            ax.set_xlabel('Kar/Zarar (%)')
            ax.set_ylabel('Coin')
            ax.set_title(f'En İyi {top_n} Coin', fontsize=self.style['title_fontsize'])
            ax.grid(True, alpha=self.style['grid_alpha'], axis='x')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.style['dpi'], bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Top coins grafiği oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Top coins grafiği oluşturma hatası: {e}")
            plt.close()
            return ""
    
    def create_hourly_distribution_chart(
        self,
        hours: List[int],
        signal_counts: List[int],
        output_path: str
    ) -> str:
        """Saatlik sinyal dağılımı"""
        try:
            fig, ax = plt.subplots(figsize=self.style['figure_size'])
            
            ax.bar(hours, signal_counts, color=self.style['colors']['primary'], **self.style['chart_types']['bar'])
            
            ax.set_xlabel('Saat')
            ax.set_ylabel('Sinyal Sayısı')
            ax.set_title('Saatlik Sinyal Dağılımı', fontsize=self.style['title_fontsize'])
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, alpha=self.style['grid_alpha'], axis='y')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.style['dpi'], bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Saatlik dağılım grafiği oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Saatlik dağılım grafiği oluşturma hatası: {e}")
            plt.close()
            return ""
    
    def create_risk_reward_scatter(
        self,
        risks: List[float],
        rewards: List[float],
        output_path: str
    ) -> str:
        """Risk/Reward scatter plot"""
        try:
            fig, ax = plt.subplots(figsize=self.style['figure_size'])
            
            scatter = ax.scatter(risks, rewards, **self.style['chart_types']['scatter'], color=self.style['colors']['primary'])
            
            # Diagonal line (1:1)
            max_val = max(max(risks), max(rewards))
            ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='1:1 Risk/Reward')
            
            ax.set_xlabel('Risk (%)')
            ax.set_ylabel('Reward (%)')
            ax.set_title('Risk/Reward Dağılımı', fontsize=self.style['title_fontsize'])
            ax.legend()
            ax.grid(True, alpha=self.style['grid_alpha'])
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=self.style['dpi'], bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Risk/Reward grafiği oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Risk/Reward grafiği oluşturma hatası: {e}")
            plt.close()
            return ""