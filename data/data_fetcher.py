import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

class DataFetcher:
    def __init__(self):
        self.cache = {}
        self.last_update = {}

    async def fetch_data(self, symbol, timeframe):
        """Belirtilen sembol ve zaman dilimi için veri çek"""
        try:
            # Önbellek kontrolü
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.cache and self.is_cache_valid(cache_key):
                print(f"Veri önbellekten alındı: {symbol} - {timeframe}")
                return self.cache[cache_key]

            # Zaman dilimi ayarları
            intervals = {
                '2m': '2m',
                '1h': '60m',
                '1d': '1d',
                '7d': '1d'
            }
            
            periods = {
                '2m': '1d',
                '1h': '5d',
                '1d': '1mo',
                '7d': '3mo'
            }

            # Yahoo Finance'den veri çek
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                period=periods.get(timeframe, '5d'),
                interval=intervals.get(timeframe, '1h')
            )

            if df.empty:
                print(f"Veri alınamadı: {symbol} - {timeframe}")
                return None

            # Index'i sıfırla ve datetime sütununu ekle
            df = df.reset_index()
            
            # Datetime sütunu kontrolü
            if 'Datetime' in df.columns:
                df = df.rename(columns={'Datetime': 'datetime'})
            elif 'Date' in df.columns:
                df = df.rename(columns={'Date': 'datetime'})
            else:
                df['datetime'] = pd.date_range(
                    end=datetime.now(),
                    periods=len(df),
                    freq=intervals.get(timeframe, '1h')
                )

            # Sütun isimlerini düzenle
            df.columns = [col.lower() for col in df.columns]
            
            # Datetime'ı index yap
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')

            # Minimum veri kontrolü
            min_rows = {
                '2m': 100,
                '1h': 24,
                '1d': 30,
                '7d': 30
            }

            if len(df) < min_rows.get(timeframe, 24):
                print(f"Yetersiz veri: {symbol} - {timeframe} (Satır sayısı: {len(df)})")
                return None

            # Veri yapısını kontrol et
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    print(f"Eksik sütun: {col}")
                    return None

            # NaN değerleri doldur
            df = df.fillna(method='ffill')
            
            # Önbelleğe kaydet
            self.cache[cache_key] = df
            self.last_update[cache_key] = datetime.now()

            print(f"Veri başarıyla alındı: {symbol} - {timeframe}")
            print(f"Sütunlar: {df.columns.tolist()}")
            print(f"Veri boyutu: {len(df)} satır")
            print(f"Tarih aralığı: {df.index.min()} - {df.index.max()}")
            
            return df

        except Exception as e:
            print(f"Veri çekme hatası ({symbol} - {timeframe}): {str(e)}")
            return None

    def is_cache_valid(self, cache_key):
        """Önbellek geçerlilik kontrolü"""
        if cache_key not in self.last_update:
            return False

        time_diff = datetime.now() - self.last_update[cache_key]
        
        if '_2m' in cache_key:
            return time_diff.seconds < 120
        elif '_1h' in cache_key:
            return time_diff.seconds < 3600
        elif '_1d' in cache_key:
            return time_diff.days < 1
        elif '_7d' in cache_key:
            return time_diff.days < 7
        
        return False

    def clear_cache(self):
        """Önbelleği temizle"""
        self.cache.clear()
        self.last_update.clear()

    def get_available_periods(self):
        """Kullanılabilir period değerleri"""
        return ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

    def get_available_intervals(self):
        """Kullanılabilir interval değerleri"""
        return ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
