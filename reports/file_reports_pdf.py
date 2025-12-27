"""
MEXC Pro Trading Bot - PDF Report Generator
Günlük PDF rapor oluşturma
"""

from datetime import datetime, timedelta
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reports.statistics import StatisticsCalculator
from reports.charts import ChartGenerator
from database.connection import get_session
from database.operations import SignalOperations
from config.settings import report_config
from utils.logger import get_logger

logger = get_logger(__name__)

class DailyReportGenerator:
    """Günlük rapor oluşturucu"""
    
    def __init__(self):
        self.report_path = Path(report_config.REPORT_PATH)
        self.report_path.mkdir(exist_ok=True)
        
        self.stats_calculator = StatisticsCalculator()
        self.chart_generator = ChartGenerator()
    
    async def generate_daily_report(self) -> str:
        """Günlük rapor oluştur"""
        try:
            logger.info("📄 Günlük rapor oluşturuluyor...")
            
            # Rapor dosya adı
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f"trading_report_{today}.pdf"
            output_path = self.report_path / filename
            
            # İstatistikleri hesapla
            daily_stats = await self.stats_calculator.calculate_daily_stats()
            
            # Sinyalleri al
            async with get_session() as session:
                start_date = datetime.now() - timedelta(days=1)
                end_date = datetime.now()
                signals = await SignalOperations.get_signals_by_date_range(
                    session, start_date, end_date
                )
            
            # PDF oluştur
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Başlık
            title = Paragraph(f"<b>Trading Raporu</b><br/>{today}", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Özet tablo
            summary_data = [
                ['Metrik', 'Değer'],
                ['Toplam Sinyal', str(daily_stats['total_signals'])],
                ['TP1 Hit', str(daily_stats['tp1_hit_count'])],
                ['Başarı Oranı', f"{daily_stats['success_rate']:.1f}%"],
                ['Ortalama Kar', f"{daily_stats['avg_profit']:.2f}%"],
                ['Max Kar', f"{daily_stats['max_profit']:.2f}%"],
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Sinyal listesi
            if signals:
                story.append(Paragraph("<b>Sinyaller</b>", styles['Heading2']))
                story.append(Spacer(1, 10))
                
                for signal in signals[:10]:  # İlk 10 sinyal
                    signal_text = f"""
                    <b>{signal.symbol}</b> - {signal.signal_type.value}<br/>
                    Skor: {signal.score:.0f} | Kaldıraç: {signal.leverage}x<br/>
                    TP1: {signal.tp1:.8f}
                    """
                    story.append(Paragraph(signal_text, styles['Normal']))
                    story.append(Spacer(1, 10))
            
            # PDF'i oluştur
            doc.build(story)
            
            logger.info(f"✅ Rapor oluşturuldu: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Rapor oluşturma hatası: {e}", exc_info=True)
            return ""