import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(data, period=14):
        if len(data) < period:
            return pd.Series(index=data.index)
            
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Başlangıç değerlerini 50 ile doldur
    
    @staticmethod
    def detect_divergence(price_data, rsi_data, window=20):
        if len(price_data) < window or len(rsi_data) < window:
            return []
            
        price_highs = []
        rsi_highs = []
        divergence = []
        
        # Son window kadar veriyi al
        for i in range(max(0, len(price_data)-window), len(price_data)):
            try:
                if i > 1 and i < len(price_data)-1:
                    # Tepe noktalarını bul
                    if (price_data[i] > price_data[i-1] and 
                        price_data[i] > price_data[i+1]):
                        price_highs.append((i, price_data[i]))
                        rsi_highs.append((i, rsi_data[i]))
                        
                        # En az iki tepe noktası varsa divergence kontrol et
                        if len(price_highs) >= 2:
                            last_price = price_highs[-1][1]
                            prev_price = price_highs[-2][1]
                            last_rsi = rsi_highs[-1][1]
                            prev_rsi = rsi_highs[-2][1]
                            
                            if last_price > prev_price and last_rsi < prev_rsi:
                                divergence.append(('bearish', i))
                            elif last_price < prev_price and last_rsi > prev_rsi:
                                divergence.append(('bullish', i))
            except IndexError:
                continue
                        
        return divergence
