import asyncio
import sys
import os
from datetime import datetime
import pytz
from config.config import Config
from utils.logger import Logger
from data.data_fetcher import DataFetcher
from analysis.trading_strategy import TradingStrategy
from analysis.risk_manager import RiskManager
from analysis.historical_analyzer import HistoricalAnalyzer
from ui.dashboard import Dashboard

# Global config ve logger tanımla
config = Config()
logger = Logger(config)

def print_menu():
    """Ana menüyü göster"""
    print("\n================================")
    print("   Crypto/Forex Trading Bot")
    print("================================\n")
    print("1. Uygulamayı Başlat")
    print("2. Bağımlılıkları Güncelle")
    print("3. Logları Temizle")
    print("4. Çıkış\n")

def get_trading_pair():
    """Kullanıcıdan trading pair seç"""
    print("\nTrading pair seçin:")
    print("1. BTC-USD (default)")
    print("2. ETH-USD")
    print("3. XRP-USD")
    print("4. Özel bir pair girin")
    
    choice = input("\nSeçiminiz (1-4) [Enter=BTC-USD]: ").strip()
    
    if not choice:  # Enter tuşuna basıldıysa
        return "BTC-USD"
    
    pairs = {
        "1": "BTC-USD",
        "2": "ETH-USD",
        "3": "XRP-USD"
    }
    
    if choice in pairs:
        return pairs[choice]
    elif choice == "4":
        custom_pair = input("Trading pair girin (örn: BTC-USD): ").strip().upper()
        return custom_pair
    else:
        print("Geçersiz seçim! BTC-USD kullanılıyor...")
        return "BTC-USD"

async def main():
    """Ana program döngüsü"""
    try:
        # Başlangıç mesajı
        logger.info("Trading Bot başlatılıyor...")
        
        # Modülleri başlat
        data_fetcher = DataFetcher()
        trading_strategy = TradingStrategy(config)
        risk_manager = RiskManager(config)
        historical_analyzer = HistoricalAnalyzer()
        dashboard = Dashboard()
        
        logger.info("Modüller başarıyla yüklendi")
        
        # Trading pair seç
        symbol = get_trading_pair()
        logger.info(f"Seçilen trading pair: {symbol}")
        
        # Ana döngü
        while True:
            try:
                logger.info("Veriler güncelleniyor...")
                
                # Verileri al
                data_2m = await data_fetcher.fetch_data(symbol, '2m')
                data_1h = await data_fetcher.fetch_data(symbol, '1h')
                data_1d = await data_fetcher.fetch_data(symbol, '1d')
                
                if data_2m is None or data_1h is None or data_1d is None:
                    logger.error("Veri alınamadı, 10 saniye sonra tekrar denenecek")
                    await asyncio.sleep(10)
                    continue
                
                logger.info(f"Veriler başarıyla alındı: {symbol}")
                logger.info(f"2m veri boyutu: {len(data_2m)}")
                logger.info(f"1h veri boyutu: {len(data_1h)}")
                logger.info(f"1d veri boyutu: {len(data_1d)}")
                
                # Tarihsel analiz
                historical_data = historical_analyzer.get_current_analysis(
                    symbol=symbol,
                    data_2m=data_2m,
                    data_1h=data_1h,
                    data_1d=data_1d
                )
                
                if historical_data:
                    logger.info(f"Tarihsel analiz tamamlandı: {symbol}")
                
                # Strateji analizi
                signals = trading_strategy.analyze_trend(data_2m, data_1h, data_1d)
                
                # Risk kontrolü
                if signals:
                    signals = risk_manager.check_signals(signals, data_1h)
                
                # Sinyalleri işle
                for signal_type, reason, confidence in signals:
                    logger.info(f"Sinyal: {symbol} - {signal_type} - {reason} - Güven: {confidence}%")
                    dashboard.add_signal(symbol, signal_type, reason, confidence)
                
                # Grafikleri güncelle
                try:
                    dashboard.create_multi_timeframe_chart(data_1h, symbol)
                    dashboard.save_and_show_chart(symbol)
                    logger.info("Grafikler güncellendi")
                except Exception as e:
                    logger.error(f"Grafik güncelleme hatası: {str(e)}")
                
                # Bekleme süresi
                logger.info(f"{config.UPDATE_INTERVAL} saniye bekleniyor...")
                await asyncio.sleep(config.UPDATE_INTERVAL)
                
            except Exception as e:
                logger.error(f"Döngü hatası: {str(e)}")
                await asyncio.sleep(10)
                
    except Exception as e:
        logger.error(f"Program hatası: {str(e)}")
        return False
    
    return True

def clean_logs():
    """Log dosyalarını temizle"""
    try:
        if os.path.exists(config.LOG_DIR):
            for file in os.listdir(config.LOG_DIR):
                if file.endswith(".log"):
                    os.remove(os.path.join(config.LOG_DIR, file))
        print("Loglar başarıyla temizlendi.")
    except Exception as e:
        print(f"Log temizleme hatası: {e}")

def update_dependencies():
    """Bağımlılıkları güncelle"""
    try:
        os.system("pip install --upgrade pip")
        os.system("pip install --upgrade -r requirements.txt")
        print("Bağımlılıklar başarıyla güncellendi.")
    except Exception as e:
        print(f"Bağımlılık güncelleme hatası: {e}")

def create_directories():
    """Gerekli klasörleri oluştur"""
    try:
        os.makedirs(config.LOG_DIR, exist_ok=True)
        os.makedirs(config.CHART_DIR, exist_ok=True)
        os.makedirs(config.DATA_DIR, exist_ok=True)
        return True
    except Exception as e:
        print(f"Klasör oluşturma hatası: {e}")
        return False

if __name__ == "__main__":
    try:
        # Klasörleri oluştur
        if not create_directories():
            sys.exit(1)
        
        while True:
            print_menu()
            choice = input("Seçiminiz (1-4): ")
            
            if choice == "1":
                # Trading Bot'u başlat
                if asyncio.run(main()):
                    print("\nProgram başarıyla tamamlandı.")
                else:
                    print("\nProgram hata ile sonlandı.")
                break
                
            elif choice == "2":
                update_dependencies()
                input("Devam etmek için bir tuşa basın...")
                
            elif choice == "3":
                clean_logs()
                input("Devam etmek için bir tuşa basın...")
                
            elif choice == "4":
                print("\nProgram sonlandırılıyor...")
                sys.exit(0)
                
            else:
                print("\nGeçersiz seçim! Lütfen tekrar deneyin.")
                input("Devam etmek için bir tuşa basın...")
                
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından sonlandırıldı.")
        sys.exit(0)
    except Exception as e:
        print(f"\nBeklenmeyen hata: {str(e)}")
        sys.exit(1)
