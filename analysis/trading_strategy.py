import pandas as pd
import numpy as np
from datetime import datetime
import logging

class TradingStrategy:
    def __init__(self, config):
        """Trading stratejisi sınıfını başlat"""
        self.config = config
        self.signals = []
        self.last_signal_time = None
        self.daily_trades = 0
        self.reset_daily_counter()
        
        # Logging ayarları
        self.logger = logging.getLogger(__name__)

    def reset_daily_counter(self):
        """Günlük işlem sayacını sıfırla"""
        now = datetime.now()
        if self.last_signal_time is None or now.date() > self.last_signal_time.date():
            self.daily_trades = 0
            self.last_signal_time = now

    def analyze_trend(self, data_2m, data_1h, data_1d):
        """Trend analizi yap"""
        try:
            self.reset_daily_counter()
            signals = []
            
            # Sütun isimlerini kontrol et ve düzelt
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for df in [data_2m, data_1h, data_1d]:
                if not all(col in df.columns for col in required_columns):
                    missing = [col for col in required_columns if col not in df.columns]
                    self.logger.error(f"Eksik sütunlar: {missing}")
                    return []
            
            # Temel göstergeler
            rsi_2m = self.calculate_rsi(data_2m['close'])
            rsi_1h = self.calculate_rsi(data_1h['close'])
            rsi_1d = self.calculate_rsi(data_1d['close'])
            
            # MACD
            macd_2m, signal_2m = self.calculate_macd(data_2m['close'])
            macd_1h, signal_1h = self.calculate_macd(data_1h['close'])
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(data_1h['close'])
            
            # Hareketli ortalamalar
            sma_short = self.calculate_sma(data_1h['close'], self.config.SMA_SHORT)
            sma_medium = self.calculate_sma(data_1h['close'], self.config.SMA_MEDIUM)
            sma_long = self.calculate_sma(data_1h['close'], self.config.SMA_LONG)
            
            # Mevcut fiyat
            current_price = data_1h['close'].iloc[-1]
            
            # Alım sinyalleri
            if self.is_buy_signal(
                current_price, rsi_2m, rsi_1h, rsi_1d,
                macd_2m, signal_2m, macd_1h, signal_1h,
                bb_lower, sma_short, sma_medium, sma_long
            ):
                confidence = self.calculate_signal_confidence("BUY", {
                    'rsi_2m': rsi_2m,
                    'rsi_1h': rsi_1h,
                    'rsi_1d': rsi_1d,
                    'macd_2m': macd_2m,
                    'signal_2m': signal_2m,
                    'macd_1h': macd_1h,
                    'signal_1h': signal_1h,
                    'price': current_price,
                    'bb_lower': bb_lower
                })
                reason = self.get_signal_reason("BUY", {
                    'rsi_2m': rsi_2m,
                    'rsi_1h': rsi_1h,
                    'macd_2m': macd_2m,
                    'signal_2m': signal_2m,
                    'price': current_price,
                    'bb_lower': bb_lower
                })
                signals.append(("BUY", reason, confidence))
            
            # Satım sinyalleri
            elif self.is_sell_signal(
                current_price, rsi_2m, rsi_1h, rsi_1d,
                macd_2m, signal_2m, macd_1h, signal_1h,
                bb_upper, sma_short, sma_medium, sma_long
            ):
                confidence = self.calculate_signal_confidence("SELL", {
                    'rsi_2m': rsi_2m,
                    'rsi_1h': rsi_1h,
                    'rsi_1d': rsi_1d,
                    'macd_2m': macd_2m,
                    'signal_2m': signal_2m,
                    'macd_1h': macd_1h,
                    'signal_1h': signal_1h,
                    'price': current_price,
                    'bb_upper': bb_upper
                })
                reason = self.get_signal_reason("SELL", {
                    'rsi_2m': rsi_2m,
                    'rsi_1h': rsi_1h,
                    'macd_2m': macd_2m,
                    'signal_2m': signal_2m,
                    'price': current_price,
                    'bb_upper': bb_upper
                })
                signals.append(("SELL", reason, confidence))
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Trend analizi hatası: {str(e)}")
            return []

    def calculate_rsi(self, prices, period=14):
        """RSI hesapla"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except Exception as e:
            self.logger.error(f"RSI hesaplama hatası: {str(e)}")
            return None

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """MACD hesapla"""
        try:
            exp1 = prices.ewm(span=fast, adjust=False).mean()
            exp2 = prices.ewm(span=slow, adjust=False).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal, adjust=False).mean()
            return macd, signal_line
        except Exception as e:
            self.logger.error(f"MACD hesaplama hatası: {str(e)}")
            return None, None

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Bollinger Bands hesapla"""
        try:
            middle_band = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = middle_band + (std_dev * std)
            lower_band = middle_band - (std_dev * std)
            return upper_band, middle_band, lower_band
        except Exception as e:
            self.logger.error(f"Bollinger Bands hesaplama hatası: {str(e)}")
            return None, None, None

    def calculate_sma(self, prices, period):
        """Basit Hareketli Ortalama hesapla"""
        try:
            return prices.rolling(window=period).mean()
        except Exception as e:
            self.logger.error(f"SMA hesaplama hatası: {str(e)}")
            return None

    def is_buy_signal(self, price, rsi_2m, rsi_1h, rsi_1d, macd_2m, signal_2m,
                     macd_1h, signal_1h, bb_lower, sma_short, sma_medium, sma_long):
        """Alım sinyali kontrol et"""
        try:
            # Günlük işlem limiti kontrolü
            if self.daily_trades >= self.config.MAX_DAILY_TRADES:
                return False
            
            # RSI koşulları
            rsi_oversold = (
                rsi_2m.iloc[-1] < self.config.RSI_OVERSOLD and
                rsi_1h.iloc[-1] < self.config.RSI_OVERSOLD
            )
            
            # MACD koşulları
            macd_crossover = (
                macd_2m.iloc[-2] < signal_2m.iloc[-2] and
                macd_2m.iloc[-1] > signal_2m.iloc[-1]
            )
            
            # Bollinger Band koşulu
            bb_bounce = price <= bb_lower.iloc[-1]
            
            # Trend koşulları
            uptrend = (
                price > sma_short.iloc[-1] and
                sma_short.iloc[-1] > sma_medium.iloc[-1] and
                sma_medium.iloc[-1] > sma_long.iloc[-1]
            )
            
            return (rsi_oversold or macd_crossover) and (bb_bounce or uptrend)
            
        except Exception as e:
            self.logger.error(f"Alım sinyali kontrolü hatası: {str(e)}")
            return False

    def is_sell_signal(self, price, rsi_2m, rsi_1h, rsi_1d, macd_2m, signal_2m,
                      macd_1h, signal_1h, bb_upper, sma_short, sma_medium, sma_long):
        """Satım sinyali kontrol et"""
        try:
            # RSI koşulları
            rsi_overbought = (
                rsi_2m.iloc[-1] > self.config.RSI_OVERBOUGHT and
                rsi_1h.iloc[-1] > self.config.RSI_OVERBOUGHT
            )
            
            # MACD koşulları
            macd_crossunder = (
                macd_2m.iloc[-2] > signal_2m.iloc[-2] and
                macd_2m.iloc[-1] < signal_2m.iloc[-1]
            )
            
            # Bollinger Band koşulu
            bb_reject = price >= bb_upper.iloc[-1]
            
            # Trend koşulları
            downtrend = (
                price < sma_short.iloc[-1] and
                sma_short.iloc[-1] < sma_medium.iloc[-1] and
                sma_medium.iloc[-1] < sma_long.iloc[-1]
            )
            
            return (rsi_overbought or macd_crossunder) and (bb_reject or downtrend)
            
        except Exception as e:
            self.logger.error(f"Satım sinyali kontrolü hatası: {str(e)}")
            return False

    def calculate_signal_confidence(self, signal_type, indicators):
        """Sinyal güven seviyesini hesapla"""
        try:
            confidence = 50  # Başlangıç güven seviyesi
            
            if signal_type == "BUY":
                # RSI analizi
                if indicators['rsi_2m'].iloc[-1] < 30: confidence += 10
                if indicators['rsi_1h'].iloc[-1] < 30: confidence += 10
                if indicators['rsi_1d'].iloc[-1] < 30: confidence += 10
                
                # MACD analizi
                if indicators['macd_2m'].iloc[-1] > indicators['signal_2m'].iloc[-1]: confidence += 10
                if indicators['macd_1h'].iloc[-1] > indicators['signal_1h'].iloc[-1]: confidence += 10
                
            elif signal_type == "SELL":
                # RSI analizi
                if indicators['rsi_2m'].iloc[-1] > 70: confidence += 10
                if indicators['rsi_1h'].iloc[-1] > 70: confidence += 10
                if indicators['rsi_1d'].iloc[-1] > 70: confidence += 10
                
                # MACD analizi
                if indicators['macd_2m'].iloc[-1] < indicators['signal_2m'].iloc[-1]: confidence += 10
                if indicators['macd_1h'].iloc[-1] < indicators['signal_1h'].iloc[-1]: confidence += 10
            
            return min(confidence, 100)  # Maximum 100%
            
        except Exception as e:
            self.logger.error(f"Güven seviyesi hesaplama hatası: {str(e)}")
            return 50

    def get_signal_reason(self, signal_type, indicators):
        """Sinyal nedenini açıkla"""
        try:
            reasons = []
            
            if signal_type == "BUY":
                if indicators['rsi_2m'].iloc[-1] < 30:
                    reasons.append("2m RSI aşırı satım")
                if indicators['rsi_1h'].iloc[-1] < 30:
                    reasons.append("1h RSI aşırı satım")
                if indicators['macd_2m'].iloc[-1] > indicators['signal_2m'].iloc[-1]:
                    reasons.append("2m MACD yukarı kesişim")
                if indicators['price'] <= indicators['bb_lower'].iloc[-1]:
                    reasons.append("Fiyat alt Bollinger bandında")
                
            elif signal_type == "SELL":
                if indicators['rsi_2m'].iloc[-1] > 70:
                    reasons.append("2m RSI aşırı alım")
                if indicators['rsi_1h'].iloc[-1] > 70:
                    reasons.append("1h RSI aşırı alım")
                if indicators['macd_2m'].iloc[-1] < indicators['signal_2m'].iloc[-1]:
                    reasons.append("2m MACD aşağı kesişim")
                if indicators['price'] >= indicators['bb_upper'].iloc[-1]:
                    reasons.append("Fiyat üst Bollinger bandında")
            
            return ", ".join(reasons) if reasons else "Teknik gösterge kombinasyonu"
            
        except Exception as e:
            self.logger.error(f"Sinyal nedeni açıklama hatası: {str(e)}")
            return "Belirsiz"
