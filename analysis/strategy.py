from .technical_indicators import TechnicalIndicators

class TradingStrategy:
    def __init__(self, config):
        self.config = config
        self.indicators = TechnicalIndicators()
        
    def generate_signals(self, data):
        signals = []
        
        # RSI hesaplama
        rsi = self.indicators.calculate_rsi(data, self.config.RSI_PERIOD)
        
        # Son değerleri al
        current_rsi = rsi.iloc[-1]
        
        # Alım-satım sinyalleri
        if current_rsi < self.config.RSI_OVERSOLD:
            signals.append(('BUY', 'RSI oversold'))
        elif current_rsi > self.config.RSI_OVERBOUGHT:
            signals.append(('SELL', 'RSI overbought'))
            
        # Divergence kontrolü
        divergences = self.indicators.detect_divergence(
            data['Close'].values,
            rsi.values
        )
        
        if divergences:
            for div_type, index in divergences:
                if div_type == 'bullish':
                    signals.append(('BUY', 'Bullish divergence'))
                else:
                    signals.append(('SELL', 'Bearish divergence'))
                    
        return signals
