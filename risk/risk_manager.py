class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_loss = 0
        self.positions = {}
        
    def calculate_position_size(self, price, account_balance):
        max_position_value = account_balance * self.config.MAX_POSITION_SIZE
        return max_position_value / price
        
    def check_stop_loss(self, symbol, current_price):
        if symbol in self.positions:
            entry_price = self.positions[symbol]['entry_price']
            position_type = self.positions[symbol]['type']
            
            if position_type == 'LONG':
                loss_percentage = (entry_price - current_price) / entry_price
                if loss_percentage >= self.config.STOP_LOSS_PERCENTAGE:
                    return True
            elif position_type == 'SHORT':
                loss_percentage = (current_price - entry_price) / entry_price
                if loss_percentage >= self.config.STOP_LOSS_PERCENTAGE:
                    return True
        return False
        
    def update_daily_loss(self, loss_amount, account_balance):
        self.daily_loss += loss_amount
        if self.daily_loss / account_balance >= self.config.MAX_DAILY_LOSS:
            return False  # Trading durdurulmalı
        return True
