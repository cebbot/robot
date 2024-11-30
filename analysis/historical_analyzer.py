import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class HistoricalAnalyzer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.support_levels = []
        self.resistance_levels = []

    def get_historical_data(self, symbol, timeframe='1h', days=365*5):
        """Tarihsel veri al"""
        try:
            # Veri alma işlemi burada yapılacak
            # Şimdilik örnek veri döndürüyoruz
            return pd.DataFrame()
        except Exception as e:
            print(f"Veri alma hatası: {e}")
            return None

    def get_current_analysis(self, symbol, data_2m, data_1h, data_1d):
        """Mevcut durum analizi"""
        try:
            analysis = {
                'support_levels': [],
                'resistance_levels': [],
                'trends': {},
                'metrics': {},
                'predictions': {}
            }
            
            # Destek ve direnç seviyeleri
            if len(data_1h) > 0:
                close_prices = data_1h['Close'].values
                analysis['support_levels'] = self.find_support_levels(close_prices)
                analysis['resistance_levels'] = self.find_resistance_levels(close_prices)
            
            # Trend analizi
            if len(data_1h) > 0:
                analysis['trends'] = {
                    'short_term': self.analyze_trend(data_2m, period=20),
                    'medium_term': self.analyze_trend(data_1h, period=50),
                    'long_term': self.analyze_trend(data_1d, period=200)
                }
            
            # Performans metrikleri
            if len(data_1h) > 0:
                analysis['metrics'] = self.calculate_metrics(data_1h)
            
            # Model tahminleri
            if self.is_trained and len(data_1h) > 0:
                analysis['predictions'] = self.predict_trend(data_1h.iloc[-1:])
            
            return analysis
            
        except Exception as e:
            print(f"Analiz hatası: {e}")
            return None

    def find_support_levels(self, prices, window=20):
        """Destek seviyeleri bul"""
        try:
            levels = []
            for i in range(window, len(prices) - window):
                if self.is_support(prices, i, window):
                    levels.append(prices[i])
            return sorted(list(set([round(level, 2) for level in levels])))
        except Exception as e:
            print(f"Destek seviyesi hesaplama hatası: {e}")
            return []

    def find_resistance_levels(self, prices, window=20):
        """Direnç seviyeleri bul"""
        try:
            levels = []
            for i in range(window, len(prices) - window):
                if self.is_resistance(prices, i, window):
                    levels.append(prices[i])
            return sorted(list(set([round(level, 2) for level in levels])))
        except Exception as e:
            print(f"Direnç seviyesi hesaplama hatası: {e}")
            return []

    def is_support(self, prices, i, window):
        """Destek noktası kontrolü"""
        support = prices[i] < prices[i - 1] and prices[i] < prices[i + 1] and \
                 prices[i + 1] < prices[i + 2] and prices[i - 1] < prices[i - 2]
        return support

    def is_resistance(self, prices, i, window):
        """Direnç noktası kontrolü"""
        resistance = prices[i] > prices[i - 1] and prices[i] > prices[i + 1] and \
                    prices[i + 1] > prices[i + 2] and prices[i - 1] > prices[i - 2]
        return resistance

    def analyze_trend(self, data, period=20):
        """Trend analizi"""
        try:
            if len(data) < period:
                return "NEUTRAL"
            
            sma = data['Close'].rolling(window=period).mean()
            current_price = data['Close'].iloc[-1]
            
            if current_price > sma.iloc[-1]:
                return "BULLISH"
            elif current_price < sma.iloc[-1]:
                return "BEARISH"
            else:
                return "NEUTRAL"
                
        except Exception as e:
            print(f"Trend analizi hatası: {e}")
            return "NEUTRAL"

    def calculate_metrics(self, data):
        """Performans metrikleri hesapla"""
        try:
            returns = data['Close'].pct_change()
            metrics = {
                'volatility': returns.std() * np.sqrt(365),
                'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(365) if returns.std() != 0 else 0,
                'max_drawdown': (data['Close'] / data['Close'].cummax() - 1).min(),
                'win_rate': len(returns[returns > 0]) / len(returns[returns != 0]) if len(returns[returns != 0]) > 0 else 0
            }
            return metrics
        except Exception as e:
            print(f"Metrik hesaplama hatası: {e}")
            return {}

    def prepare_features(self, data):
        """Özellik hazırlama"""
        try:
            df = data.copy()
            
            # Teknik göstergeler
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = self.calculate_rsi(df['Close'])
            df['MACD'], df['Signal'] = self.calculate_macd(df['Close'])
            
            # Özellik seçimi
            features = df[['SMA20', 'SMA50', 'RSI', 'MACD', 'Signal']].fillna(0)
            return features
            
        except Exception as e:
            print(f"Özellik hazırlama hatası: {e}")
            return None

    def calculate_rsi(self, prices, period=14):
        """RSI hesapla"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except Exception as e:
            print(f"RSI hesaplama hatası: {e}")
            return pd.Series(0, index=prices.index)

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """MACD hesapla"""
        try:
            exp1 = prices.ewm(span=fast, adjust=False).mean()
            exp2 = prices.ewm(span=slow, adjust=False).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal, adjust=False).mean()
            return macd, signal_line
        except Exception as e:
            print(f"MACD hesaplama hatası: {e}")
            return pd.Series(0, index=prices.index), pd.Series(0, index=prices.index)
