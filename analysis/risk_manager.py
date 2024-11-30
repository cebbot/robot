from datetime import datetime, timedelta
import pytz

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.trade_history = {}  # Sembol bazlı işlem geçmişi
        self.daily_trades = {}   # Günlük işlem sayısı
        
    def check_position_allowed(self, symbol, signal_type):
        """Yeni pozisyon açılmasına izin verilip verilmediğini kontrol et"""
        try:
            current_time = datetime.now(pytz.UTC)
            current_date = current_time.date()
            
            # Günlük işlem limitini kontrol et
            if current_date not in self.daily_trades:
                self.daily_trades[current_date] = 0
            
            if self.daily_trades[current_date] >= self.config.MAX_DAILY_TRADES:
                return False
            
            # Son işlemden bu yana geçen süreyi kontrol et
            if symbol in self.trade_history:
                last_trade_time = self.trade_history[symbol]['timestamp']
                min_time_between_trades = timedelta(minutes=self.config.MIN_TIME_BETWEEN_TRADES)
                
                if current_time - last_trade_time < min_time_between_trades:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Risk kontrolü hatası: {e}")
            return False
    
    def update_trade_history(self, symbol, signal_type):
        """İşlem geçmişini güncelle"""
        try:
            current_time = datetime.now(pytz.UTC)
            current_date = current_time.date()
            
            # İşlem geçmişini güncelle
            self.trade_history[symbol] = {
                'type': signal_type,
                'timestamp': current_time
            }
            
            # Günlük işlem sayısını güncelle
            if current_date not in self.daily_trades:
                self.daily_trades[current_date] = 0
            self.daily_trades[current_date] += 1
            
        except Exception as e:
            print(f"İşlem geçmişi güncelleme hatası: {e}")
