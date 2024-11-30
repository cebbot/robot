import os
from datetime import datetime
import logging
from pathlib import Path

class Config:
    def __init__(self):
        """Yapılandırma sınıfını başlat"""
        # Temel dizinler
        self.BASE_DIR = Path(__file__).parent
        self.LOG_DIR = self.BASE_DIR / 'logs'
        self.CHART_DIR = self.BASE_DIR / 'charts'
        
        # Dizinleri oluştur
        self.LOG_DIR.mkdir(exist_ok=True)
        self.CHART_DIR.mkdir(exist_ok=True)
        
        # Log ayarları
        self.LOG_LEVEL = 'INFO'
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        self.LOG_FILE = self.LOG_DIR / f'trading_bot_{datetime.now().strftime("%Y%m%d")}.log'
        
        # Trading çiftleri
        self.TRADING_PAIRS = {
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum',
            'XRP-USD': 'Ripple'
        }
        
        # Veri ayarları
        self.TIMEFRAMES = {
            '2m': {'period': '1d', 'interval': '2m'},
            '1h': {'period': '5d', 'interval': '60m'},
            '1d': {'period': '1mo', 'interval': '1d'}
        }
        
        # Teknik gösterge ayarları
        self.RSI_PERIOD = 14
        self.RSI_OVERSOLD = 30
        self.RSI_OVERBOUGHT = 70
        
        self.MACD_FAST = 12
        self.MACD_SLOW = 26
        self.MACD_SIGNAL = 9
        
        self.BB_PERIOD = 20
        self.BB_STD = 2
        
        self.SMA_SHORT = 20
        self.SMA_MEDIUM = 50
        self.SMA_LONG = 200
        
        # Grafik ayarları
        self.PRICE_COLUMNS = ['open', 'high', 'low', 'close']
        self.VOLUME_COLUMN = 'volume'
        self.DATETIME_COLUMN = 'datetime'
        
        # Trading ayarları
        self.MAX_DAILY_TRADES = 5
        self.MIN_TRADE_INTERVAL = 3600  # saniye
        self.CONFIDENCE_THRESHOLD = 70
        
        # API ayarları
        self.API_RETRY_COUNT = 3
        self.API_RETRY_DELAY = 5
        self.API_TIMEOUT = 30
        
        # Cache ayarları
        self.CACHE_DURATION = {
            '2m': 120,    # 2 dakika
            '1h': 3600,   # 1 saat
            '1d': 86400   # 1 gün
        }
        
        # Renk ayarları
        self.COLORS = {
            'background': '#0f1015',
            'text': '#ffffff',
            'grid': '#1e222d',
            'buy': '#26a69a',
            'sell': '#ef5350',
            'volume_up': '#26a69a',
            'volume_down': '#ef5350',
            'ma20': '#f5d142',
            'ma50': '#ff69b4',
            'ma200': '#ce93d8'
        }
        
        # Grafik stil ayarları
        self.CHART_STYLE = {
            'template': 'plotly_dark',
            'height': 800,
            'margin': dict(l=50, r=50, t=50, b=50)
        }
        
        # Logging ayarları
        self.setup_logging()

    def setup_logging(self):
        """Logging ayarlarını yapılandır"""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format=self.LOG_FORMAT,
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        
        # Gereksiz uyarıları kapat
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('matplotlib').setLevel(logging.WARNING)

    def get_trading_pairs(self):
        """Trading çiftlerini getir"""
        return list(self.TRADING_PAIRS.keys())

    def get_pair_name(self, symbol):
        """Trading çifti adını getir"""
        return self.TRADING_PAIRS.get(symbol, symbol)

    def get_timeframe_settings(self, timeframe):
        """Zaman dilimi ayarlarını getir"""
        return self.TIMEFRAMES.get(timeframe, {})

    def get_cache_duration(self, timeframe):
        """Önbellek süresini getir"""
        return self.CACHE_DURATION.get(timeframe, 300)  # varsayılan 5 dakika

    def get_price_columns(self):
        """Fiyat sütunlarını getir"""
        return self.PRICE_COLUMNS

    def get_volume_column(self):
        """Hacim sütununu getir"""
        return self.VOLUME_COLUMN

    def get_datetime_column(self):
        """Tarih sütununu getir"""
        return self.DATETIME_COLUMN

    def get_chart_style(self):
        """Grafik stilini getir"""
        return self.CHART_STYLE

    def get_colors(self):
        """Renk şemasını getir"""
        return self.COLORS

    def get_indicator_settings(self):
        """Gösterge ayarlarını getir"""
        return {
            'rsi': {
                'period': self.RSI_PERIOD,
                'oversold': self.RSI_OVERSOLD,
                'overbought': self.RSI_OVERBOUGHT
            },
            'macd': {
                'fast': self.MACD_FAST,
                'slow': self.MACD_SLOW,
                'signal': self.MACD_SIGNAL
            },
            'bollinger': {
                'period': self.BB_PERIOD,
                'std': self.BB_STD
            },
            'sma': {
                'short': self.SMA_SHORT,
                'medium': self.SMA_MEDIUM,
                'long': self.SMA_LONG
            }
        }

    def get_trading_settings(self):
        """Trading ayarlarını getir"""
        return {
            'max_daily_trades': self.MAX_DAILY_TRADES,
            'min_trade_interval': self.MIN_TRADE_INTERVAL,
            'confidence_threshold': self.CONFIDENCE_THRESHOLD
        }

    def get_api_settings(self):
        """API ayarlarını getir"""
        return {
            'retry_count': self.API_RETRY_COUNT,
            'retry_delay': self.API_RETRY_DELAY,
            'timeout': self.API_TIMEOUT
        }
