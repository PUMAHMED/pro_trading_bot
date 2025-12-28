"""
MEXC Pro Trading Bot - PDF Report Generator
Günlük PDF rapor oluşturma modülü
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from database.connection import get_session
from database.operations import SignalOperations, PerformanceOperations
from reports.charts import ChartGenerator
from reports.statistics import StatisticsCalculator
from config.settings import report_config
from config.constants import REPORT_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)


class DailyReportGenerator:
    """Günlük PDF rapor oluşturucu"""
    
    def __init__(self):
        self.config = report_config
        self.chart_generator = ChartGenerator()
        self.statistics_calculator = StatisticsCalculator()
        
        self.report_dir = Path(self.config.REPORT_PATH)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_dir = self.report_dir / 'temp'
        self.temp_dir.mkdir(exist_ok=True)
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        logger.info("✅ DailyReportGenerator başlatıldı")
    
    def _setup_custom_styles(self):
        """Özel stil tanımlamaları"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=REPORT_CONFIG['fonts']['title'],
            textColor=colors.HexColor(REPORT_CONFIG['colors']['primary']),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=REPORT_CONFIG['fonts']['heading'],
            textColor=colors.HexColor(REPORT_CONFIG['colors']['primary']),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=REPORT_CONFIG['fonts']['body'],
            spaceAfter=6
        ))
    
    async def generate_daily_report(self, date: Optional[datetime] = None) -> str:
        """Günlük rapor oluştur"""
        try:
            if date is None:
                date = datetime.now()
            
            date_str = date.strftime('%Y-%m-%d')
            report_filename = f"daily_report_{date_str}.pdf"
            report_path = self.report_dir / report_filename
            
            logger.info(f"📄 Günlük rapor oluşturuluyor: {date_str}")
            
            # Veri toplama
            async with get_session() as session:
                start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
                
                signals = await SignalOperations.get_signals_by_date_range(session, start_date, end_date)
                statistics = await SignalOperations.get_signal_statistics(session, days=1)
            
            # İstatistikler hesapla
            stats = await self.statistics_calculator.calculate_daily_statistics(signals)
            
            # Grafikler oluştur
            charts = await self._generate_charts(signals, stats, date_str)
            
            # PDF oluştur
            doc = SimpleDocTemplate(
                str(report_path),
                pagesize=A4,
                topMargin=REPORT_CONFIG['margins']['top'],
                bottomMargin=REPORT_CONFIG['margins']['bottom'],
                leftMargin=REPORT_CONFIG['margins']['left'],
                rightMargin=REPORT_CONFIG['margins']['right']
            )
            
            story = []
            
            # Başlık
            story.append(Paragraph(f"MEXC Pro Trading Bot - Günlük Rapor", self.styles['CustomTitle']))
            story.append(Paragraph(f"Tarih: {date_str}", self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Genel özet
            story.extend(self._create_summary_section(statistics, stats))
            story.append(Spacer(1, 0.2*inch))
            
            # Performans grafiği
            if charts.get('performance'):
                story.append(Paragraph("Performans Grafiği", self.styles['CustomHeading']))
                story.append(Image(charts['performance'], width=6*inch, height=4*inch))
                story.append(Spacer(1, 0.2*inch))
            
            # Sinyal detayları
            if signals:
                story.extend(self._create_signals_section(signals[:10]))
                story.append(PageBreak())
            
            # Win rate grafiği
            if charts.get('win_rate'):
                story.append(Paragraph("Başarı Oranları", self.styles['CustomHeading']))
                story.append(Image(charts['win_rate'], width=5*inch, height=5*inch))
                story.append(Spacer(1, 0.2*inch))
            
            # Top performers
            if charts.get('top_coins'):
                story.append(Paragraph("En İyi Performans Gösteren Coinler", self.styles['CustomHeading']))
                story.append(Image(charts['top_coins'], width=6*inch, height=5*inch))
                story.append(Spacer(1, 0.2*inch))
            
            # Öneriler
            story.extend(self._create_recommendations_section(stats))
            
            # PDF'i oluştur
            doc.build(story)
            
            # Temp dosyaları temizle
            self._cleanup_temp_files(charts)
            
            logger.info(f"✅ Günlük rapor oluşturuldu: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"❌ Rapor oluşturma hatası: {e}", exc_info=True)
            return ""
    
    async def _generate_charts(self, signals: List, stats: Dict[str, Any], date_str: str) -> Dict[str, str]:
        """Grafikleri oluştur"""
        charts = {}
        
        try:
            # Performans grafiği
            if signals:
                dates = [s.created_at for s in signals]
                profits = [s.actual_profit_percent or 0 for s in signals]
                charts['performance'] = self.chart_generator.create_performance_chart(
                    dates, profits, str(self.temp_dir / f'performance_{date_str}.png')
                )
            
            # Win rate grafiği
            tp1_count = stats.get('tp1_count', 0)
            tp2_count = stats.get('tp2_count', 0)
            sl_count = stats.get('sl_count', 0)
            
            if tp1_count + tp2_count + sl_count > 0:
                charts['win_rate'] = self.chart_generator.create_win_rate_chart(
                    ['TP1 Hit', 'TP2 Hit', 'SL Hit'],
                    [tp1_count, tp2_count, sl_count],
                    str(self.temp_dir / f'win_rate_{date_str}.png')
                )
            
            # Top coins grafiği
            if stats.get('top_coins'):
                coins = [c['symbol'] for c in stats['top_coins']]
                profits = [c['profit'] for c in stats['top_coins']]
                charts['top_coins'] = self.chart_generator.create_top_coins_chart(
                    coins, profits, str(self.temp_dir / f'top_coins_{date_str}.png')
                )
            
        except Exception as e:
            logger.error(f"❌ Grafik oluşturma hatası: {e}")
        
        return charts
    
    def _create_summary_section(self, statistics: Dict[str, Any], stats: Dict[str, Any]) -> List:
        """Özet bölümü oluştur"""
        elements = []
        
        elements.append(Paragraph("📊 Genel Özet", self.styles['CustomHeading']))
        
        summary_data = [
            ['Metrik', 'Değer'],
            ['Toplam Sinyal', str(statistics.get('total_signals', 0))],
            ['TP1 Hit', str(statistics.get('tp1_hit_count', 0))],
            ['TP2 Hit', str(statistics.get('tp2_hit_count', 0))],
            ['TP3 Hit', str(statistics.get('tp3_hit_count', 0))],
            ['SL Hit', str(statistics.get('sl_hit_count', 0))],
            ['Başarı Oranı', f"{statistics.get('success_rate', 0):.1f}%"],
            ['Ortalama Kar', f"{statistics.get('avg_profit', 0):.2f}%"],
            ['Maksimum Kar', f"{statistics.get('max_profit', 0):.2f}%"],
            ['Ortalama Süre', f"{statistics.get('avg_duration_minutes', 0):.0f} dakika"]
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(REPORT_CONFIG['colors']['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), REPORT_CONFIG['fonts']['body']),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def _create_signals_section(self, signals: List) -> List:
        """Sinyal detayları bölümü"""
        elements = []
        
        elements.append(Paragraph("📈 Sinyal Detayları (İlk 10)", self.styles['CustomHeading']))
        
        signal_data = [['Coin', 'Yön', 'Entry', 'TP1', 'SL', 'Leverage', 'Skor', 'Durum']]
        
        for signal in signals:
            signal_data.append([
                signal.symbol,
                signal.signal_type.value,
                f"${signal.entry_price:.6f}",
                f"${signal.tp1:.6f}",
                f"${signal.stop_loss:.6f}",
                f"{signal.leverage}x",
                f"{signal.score:.0f}",
                signal.status.value
            ])
        
        table = Table(signal_data, colWidths=[0.8*inch]*8)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(REPORT_CONFIG['colors']['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), REPORT_CONFIG['fonts']['small']),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
        return elements
    
    def _create_recommendations_section(self, stats: Dict[str, Any]) -> List:
        """Öneriler bölümü"""
        elements = []
        
        elements.append(Paragraph("💡 Öneriler ve İyileştirmeler", self.styles['CustomHeading']))
        
        recommendations = []
        
        success_rate = stats.get('overall_success_rate', 0)
        if success_rate < 50:
            recommendations.append("Başarı oranı düşük. Sinyal kalite eşiğini yükseltmeyi düşünün.")
        elif success_rate > 70:
            recommendations.append("Mükemmel başarı oranı. Mevcut stratejiye devam edilebilir.")
        
        avg_profit = stats.get('avg_profit', 0)
        if avg_profit < 2:
            recommendations.append("Ortalama kar düşük. TP seviyelerini revize edin.")
        
        total_signals = stats.get('total_signals', 0)
        if total_signals < 5:
            recommendations.append("Düşük sinyal sayısı. Filtreleri gevşetmeyi düşünün.")
        elif total_signals > 50:
            recommendations.append("Yüksek sinyal sayısı. Kalite filtreleri daha sıkı yapılabilir.")
        
        if not recommendations:
            recommendations.append("Tüm metrikler normal aralıkta. İyi iş çıkarıyorsunuz!")
        
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _cleanup_temp_files(self, charts: Dict[str, str]):
        """Geçici dosyaları temizle"""
        try:
            for chart_path in charts.values():
                if chart_path and os.path.exists(chart_path):
                    os.remove(chart_path)
        except Exception as e:
            logger.warning(f"⚠️ Temp dosya temizleme hatası: {e}")