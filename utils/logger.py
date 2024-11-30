import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('TradingBot')
        self.logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # Log dosyası adını oluştur
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = self.config.LOG_FILE.format(date=date_str)
        log_path = os.path.join(self.config.LOG_DIR, log_file)
        
        # Dosya handler'ı oluştur
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # Console handler'ı oluştur
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # Formatter oluştur
        formatter = logging.Formatter(self.config.LOG_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Handler'ları ekle
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log dosyasının yolunu kaydet
        self.log_file = log_path
        
        # Başlangıç mesajı
        self.info(f"Log dosyası: {self.log_file}")

    def info(self, message):
        """Bilgi mesajı logla"""
        self.logger.info(message)

    def error(self, message):
        """Hata mesajı logla"""
        self.logger.error(message)

    def warning(self, message):
        """Uyarı mesajı logla"""
        self.logger.warning(message)

    def debug(self, message):
        """Debug mesajı logla"""
        self.logger.debug(message)

    def get_log_file(self):
        """Log dosyasının yolunu döndür"""
        return self.log_file
