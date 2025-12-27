# 🚀 MEXC Pro Trading Bot

Profesyonel kripto trading sinyal botu. MEXC ve Binance exchange'lerini tarar, gelişmiş teknik analiz yapar ve Telegram üzerinden yüksek kaliteli sinyaller gönderir.

## 🎯 Özellikler

### 🔍 Tarama ve Analiz
- ✅ **Çoklu Exchange Desteği**: MEXC ve Binance'deki tüm USDT paritelerini tarar
- ✅ **Otomatik Coin Keşfi**: Yeni eklenen coinleri otomatik tespit eder
- ✅ **Paralel Tarama**: 100+ coini aynı anda tarayabilir (30 saniye interval)
- ✅ **Çoklu Timeframe Analizi**: 5m, 15m, 1h, 4h timeframe'lerde analiz

### 📊 Teknik Analiz
- **İndikatörler**: RSI, MACD, Bollinger Bands, EMA/SMA crossover, Ichimoku
- **Volume Analizi**: Volume profil, OBV, Money Flow Index, alım/satım baskısı
- **Pattern Recognition**: Double top/bottom, Head & Shoulders, Triangle, Flag, Wedge
- **Support/Resistance**: Otomatik S/R seviyeleri tespiti
- **Order Book Analizi**: Liquidity walls, depth imbalance, spread kontrolü

### 🔐 Manipülasyon Tespiti
- **Pump/Dump Detection**: Anormal fiyat ve volume hareketleri tespiti
- **Wash Trading**: Sahte volume tespiti
- **Spoofing**: Sahte order tespiti
- **Liquidity Hunt**: Stop loss hunting tespiti
- **Balina Takibi**: Büyük orderların analizi
- **Konsolidasyon Kontrolü**: Minimum 2 saat stabil hareket gereksinimi

### 🤖 Machine Learning
- **Tahminleme**: Geçmiş verilerden öğrenerek yön ve hareket tahmini
- **Feature Engineering**: 25+ teknik ve fundamental özellik
- **Model Eğitimi**: Otomatik model güncelleme
- **Confidence Scoring**: Tahmin güvenilirlik skoru

### 📈 Sinyal Özellikleri
- **Hedef**: Minimum %4 kar (TP1), dinamik TP2 ve TP3
- **Stop Loss**: Dinamik SL hesaplama (support/resistance bazlı)
- **Kaldıraç**: 20x-500x arası akıllı kaldıraç önerisi
- **Kalite Skorlama**: 0-100 arası sinyal kalite skoru
- **Zaman Tahmini**: Hedefe ulaşma süre tahmini
- **Risk Seviyesi**: Düşük/Orta/Yüksek risk kategorilendirmesi

### 🎯 Filtreleme
- Minimum $500K günlük volume
- %2-50 arası volatilite
- Sıkı spread kontrolü (max %0.5)
- Likidite derinliği kontrolü
- Sahte hareket filtreleme

### 📱 Telegram Bot
- **İnteraktif Menü**: Buton bazlı kolay kullanım
- **Özelleştirilebilir Bildirimler**: Tercih bazlı sinyal filtreleme
- **Manuel Analiz**: İstediğiniz coin'i analiz ettirme
- **Canlı İstatistikler**: Gerçek zamanlı performans takibi
- **Ayarlar**: Bildirim, filtre ve risk ayarlarını özelleştirme

### 📄 Raporlama
- **Günlük PDF Rapor**: Otomatik oluşturulan detaylı raporlar
- **Grafikler**: Performans ve win rate grafikleri
- **İstatistikler**: Başarı oranı, kar/zarar, süre analizleri
- **Top Performers**: En iyi coin'ler
- **AI Insights**: Yapay zeka destekli öneriler

## 📋 Gereksinimler

- Python 3.11+
- PostgreSQL (Railway otomatik sağlar)
- Telegram Bot Token
- MEXC API Keys (read-only yeterli)
- Binance API Keys (read-only yeterli)

## 🚀 Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone <your-repo-url>
cd mexc-pro-bot
```

### 2. Environment Variables Ayarlayın

`.env` dosyası oluşturun:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin ve gerekli API key'leri ekleyin.

### 3. Railway'de Deploy

1. [Railway.app](https://railway.app)'e gidin
2. "New Project" → "Deploy from GitHub repo"
3. Repository'nizi seçin
4. Environment variables ekleyin (`.env.example`'dan)
5. **Add Plugin** → **PostgreSQL** ekleyin
6. Deploy!

Railway otomatik olarak:
- PostgreSQL database oluşturacak
- Environment variables ayarlayacak
- Bot'u çalıştıracak

### 4. Local Development (Opsiyonel)

```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Database
python -c "from database.connection import init_database; import asyncio; asyncio.run(init_database())"

# Run
python main.py
```

## 🎮 Kullanım

### Telegram Komutları

- `/start` - Bot'u başlat ve ana menüyü göster
- `/help` - Yardım ve komut listesi
- `/status` - Bot durumu ve sistem sağlığı
- `/stats` - Günlük performans istatistikleri
- `/analyze SYMBOL` - Manuel coin analizi (örn: `/analyze BTC/USDT`)
- `/settings` - Ayarlar menüsü
- `/report` - Günlük raporu al

### Ana Menü Butonları

📊 **İstatistikler**: Günlük/haftalık performans  
🔍 **Manuel Analiz**: İstediğiniz coin'i analiz ettirin  
⚙️ **Ayarlar**: Bot ayarlarını özelleştirin  
📄 **Günlük Rapor**: PDF raporu indirin  
🔔 **Bildirimler**: Bildirim tercihlerini ayarlayın  
ℹ️ **Sistem Durumu**: Bot sağlık ve uptime bilgisi

### Ayarlar

**Bildirim Ayarları:**
- Tüm sinyalleri al / Sadece yüksek kalite
- TP bildirimleri aktif/pasif
- SL uyarıları aktif/pasif
- Analiz güncelleme bildirimleri

**Sinyal Filtreleri:**
- Minimum sinyal skoru (70/80/90)
- Exchange seçimi (MEXC/Binance/Her ikisi)
- Yön filtreleme (LONG/SHORT/Her ikisi)

**Risk Ayarları:**
- Maximum kaldıraç limiti (50x/100x/200x)
- Risk toleransı (Düşük/Orta/Yüksek)

## 📊 Sinyal Formatı

```
🔥 MÜKEMMEL SİNYAL - MEXC

💎 Coin: BTC/USDT
📊 Yön: LONG
💰 Fiyat: $45,230.50

🎯 Hedefler:
  TP1: $47,039.72 (+4.0%)
  TP2: $48,848.94 (+8.0%)
  TP3: $50,658.16 (+12.0%)

🛡️ Stop Loss: $44,325.89 (-2.0%)
⚡ Kaldıraç: 50x

⏰ Tahmini Süre: 2-4 saat
📈 Sinyal Skoru: 92/100
🧠 Güven: YÜKSEK

📊 Analiz Özeti:
✅ Güçlü yükseliş trendi
✅ RSI oversold'dan çıkıyor
✅ MACD bullish crossover
✅ Yüksek volume desteği
✅ Support seviyesinde

⚠️ Risk: ORTA
```

## 🏗️ Proje Yapısı

```
mexc-pro-bot/
├── main.py                 # Ana entry point
├── config/                 # Konfigürasyon
│   ├── settings.py         # Tüm ayarlar
│   ├── constants.py        # Sabitler ve enum'lar
│   └── exchanges.py        # Exchange configs
├── database/               # Database layer
│   ├── models.py           # SQLAlchemy modelleri
│   ├── operations.py       # CRUD işlemleri
│   └── connection.py       # DB bağlantı yönetimi
├── exchanges/              # Exchange API clients
│   ├── mexc_client.py      # MEXC API
│   ├── binance_client.py   # Binance API
│   └── whale_tracker.py    # Balina takibi
├── core/                   # Ana iş mantığı
│   ├── scanner.py          # Coin tarama motoru
│   ├── analyzer.py         # Market analiz koordinatörü
│   ├── signal_generator.py # Sinyal üretimi
│   ├── risk_manager.py     # Risk yönetimi
│   └── ml_engine.py        # ML tahminleme
├── analyzers/              # Analiz modülleri
│   ├── technical.py        # Teknik analiz
│   ├── volume.py           # Volume analizi
│   ├── orderbook.py        # Order book analizi
│   ├── pattern.py          # Pattern recognition
│   ├── manipulation.py     # Manipülasyon tespiti
│   └── historical.py       # Geçmiş veri analizi
├── bot/                    # Telegram bot
│   ├── telegram_bot.py     # Ana bot sınıfı
│   ├── handlers.py         # Komut handler'ları
│   ├── keyboards.py        # Inline keyboard'lar
│   └── notifications.py    # Bildirim yönetimi
├── reports/                # Raporlama
│   ├── pdf_generator.py    # PDF oluşturma
│   ├── charts.py           # Grafik oluşturma
│   └── statistics.py       # İstatistik hesaplama
└── utils/                  # Yardımcı fonksiyonlar
    ├── logger.py           # Logging
    ├── cache.py            # Cache yönetimi
    ├── helpers.py          # Helper fonksiyonlar
    └── performance.py      # Performans monitoring
```

## 🔧 Konfigürasyon

Tüm ayarlar `config/settings.py` dosyasında bulunur:

**Trading:**
- TP1/TP2/TP3 hedefleri
- Stop loss limitleri
- Kaldıraç aralıkları
- Günlük maksimum sinyal sayısı

**Scanner:**
- Tarama intervali
- Minimum volume
- Volatilite aralığı
- Quote currencies

**Analiz:**
- İndikatör periyotları
- Sinyal kalite eşikleri
- Timeframe'ler

**Manipülasyon:**
- Pump/dump eşikleri
- Konsolidasyon gereksinimleri
- Spread limitleri
- Whale thresholds

## 📈 Performans

- **Hız**: 100+ coin paralel tarama, 30 saniye interval
- **Verimlilik**: Async/await ile non-blocking operations
- **Cache**: Redis ile hızlı data erişimi (opsiyonel)
- **Database**: Connection pooling ile optimize edilmiş sorgular
- **Rate Limit**: Akıllı rate limit yönetimi

## 🛡️ Güvenlik

- API keys sadece **read-only** yetkileri gerektirir
- Environment variables ile credential yönetimi
- Rate limit koruması
- Kapsamlı error handling
- Secure database bağlantıları

## ⚠️ Önemli Uyarılar

1. **Bu bot SADECE sinyal verir, otomatik işlem AÇMAZ**
2. **Tüm trading kararları kullanıcıya aittir**
3. **Kripto trading son derece risklidir**
4. **Sadece kaybetmeyi göze alabileceğiniz sermaye ile trade yapın**
5. **Geçmiş performans gelecek sonuçları garanti etmez**
6. **Bot'un sinyalleri kesin kar garantisi DEĞİLDİR**

## 📝 Lisans

MIT License

## 🤝 Destek

Sorularınız için:
- GitHub Issues
- Telegram: /help komutu

---

**Made with ❤️ for crypto traders**

⭐ Projeyi beğendiyseniz star vermeyi unutmayın!
