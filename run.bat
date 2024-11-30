@echo off
SETLOCAL EnableDelayedExpansion

:: Doğru dizine git
cd /d "%~dp0"

:: Başlık ve renk ayarları
title Crypto/Forex Trading Bot
color 0A

:: Mevcut dizini yazdır
echo Çalışma dizini: %CD%

:: Config dosyası kontrolü
echo Config dosyası kontrol ediliyor...
if exist "config\config.py" (
    echo Config dosyası bulundu: config\config.py
) else (
    echo Config dosyası bulunamadı: config\config.py
    echo Dosya yolu: %CD%\config\config.py
    pause
    exit
)

:: Python kontrolü
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python kurulu...
    python --version
) else (
    echo Python kurulu değil! Lütfen Python 3.8 veya üstünü yükleyin.
    echo https://www.python.org/downloads/
    pause
    exit
)

:: Virtual environment kontrolü ve kurulumu
if not exist "venv" (
    echo Virtual environment oluşturuluyor...
    python -m venv venv
    if %errorLevel% == 0 (
        echo Virtual environment başarıyla oluşturuldu.
    ) else (
        echo Virtual environment oluşturulurken hata oluştu!
        pause
        exit
    )
)

:: Virtual environment'ı aktifleştir
echo Virtual environment aktifleştiriliyor...
call venv\Scripts\activate

:: Pip'i güncelle
python -m pip install --upgrade pip

:: Gerekli kütüphanelerin kontrolü ve kurulumu
echo Gerekli kütüphaneler kontrol ediliyor...

:: Kütüphaneleri yükle
pip install -r requirements.txt
if %errorLevel% == 0 (
    echo Kütüphaneler başarıyla yüklendi/güncellendi.
) else (
    echo Kütüphaneler yüklenirken hata oluştu!
    pause
    exit
)

:: Logs klasörü kontrolü
if not exist "logs" mkdir logs

:: Uygulamayı başlat
:start
cls
echo.
echo ================================
echo    Crypto/Forex Trading Bot
echo ================================
echo.
echo 1. Uygulamayı Başlat
echo 2. Bağımlılıkları Güncelle
echo 3. Logları Temizle
echo 4. Çıkış
echo.
set /p choice="Seçiminiz (1-4): "

if "%choice%"=="1" (
    echo.
    echo Trading Bot başlatılıyor...
    echo Log dosyası: logs\trading_bot_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log
    python main.py
    if %errorLevel% == 0 (
        echo.
        echo Program başarıyla tamamlandı.
    ) else (
        echo.
        echo Program çalışırken bir hata oluştu!
        echo Detaylar için log dosyasını kontrol edin.
    )
    pause
    goto start
)

if "%choice%"=="2" (
    echo.
    echo Bağımlılıklar güncelleniyor...
    pip install --upgrade -r requirements.txt
    pause
    goto start
)

if "%choice%"=="3" (
    echo.
    echo Loglar temizleniyor...
    del /Q logs\*
    echo Loglar temizlendi.
    pause
    goto start
)

if "%choice%"=="4" (
    echo.
    echo Uygulama kapatılıyor...
    timeout /t 2 >nul
    exit
)

echo.
echo Geçersiz seçim!
pause
goto start

ENDLOCAL