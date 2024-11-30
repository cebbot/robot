import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.express as px
import warnings
import pytz
from pathlib import Path

# Matplotlib uyarılarını kapat
warnings.filterwarnings('ignore')

class Dashboard:
    def __init__(self):
        """Dashboard sınıfını başlat"""
        self.signals = []
        self.charts = {}
        self.last_update = None
        
        # Grafik klasörünü oluştur
        os.makedirs('charts', exist_ok=True)
        
        # Stil ayarları
        self.colors = {
            'background': '#0f1015',
            'text': '#ffffff',
            'grid': '#1e222d',
            'buy': '#26a69a',
            'sell': '#ef5350',
            'volume_up': '#26a69a',
            'volume_down': '#ef5350',
            'ma20': '#f5d142',
            'ma50': '#ff69b4',
            'ma200': '#ce93d8'
        }
        
        # Grafik ayarları
        self.chart_config = {
            'template': 'plotly_dark',
            'height': 800,
            'margin': dict(l=50, r=50, t=50, b=50)
        }

    def add_signal(self, symbol, signal_type, reason, confidence):
        """Sinyal ekle"""
        try:
            signal = {
                'symbol': symbol,
                'type': signal_type,
                'reason': reason,
                'confidence': confidence,
                'timestamp': datetime.now(pytz.UTC)
            }
            self.signals.append(signal)
            print(f"Yeni sinyal eklendi: {signal_type} {symbol} ({confidence}% güven)")
            return True
        except Exception as e:
            print(f"Sinyal ekleme hatası: {str(e)}")
            return False

    def create_multi_timeframe_chart(self, data, symbol):
        """Çoklu zaman dilimli grafik oluştur"""
        try:
            # Alt grafikler için figure oluştur
            fig = make_subplots(
                rows=3, 
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.6, 0.2, 0.2],
                subplot_titles=(
                    f'{symbol} Fiyat Grafiği',
                    'Hacim',
                    'RSI'
                )
            )

            # Mum grafiği ekle
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name='OHLC',
                    increasing_line_color=self.colors['buy'],
                    decreasing_line_color=self.colors['sell']
                ),
                row=1, col=1
            )

            # Hacim grafiği ekle
            colors = [self.colors['volume_up'] if row['close'] >= row['open'] 
                     else self.colors['volume_down'] 
                     for _, row in data.iterrows()]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['volume'],
                    name='Hacim',
                    marker_color=colors,
                    opacity=0.8
                ),
                row=2, col=1
            )

            # Hareketli ortalamalar ekle
            ma_periods = {
                'MA20': (20, self.colors['ma20']),
                'MA50': (50, self.colors['ma50']),
                'MA200': (200, self.colors['ma200'])
            }
            
            for name, (period, color) in ma_periods.items():
                ma = data['close'].rolling(window=period).mean()
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=ma,
                        name=name,
                        line=dict(
                            color=color,
                            width=1
                        )
                    ),
                    row=1, col=1
                )

            # RSI göstergesi ekle
            rsi = self.calculate_rsi(data['close'])
            if rsi is not None:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=rsi,
                        name='RSI',
                        line=dict(
                            color='white',
                            width=1
                        )
                    ),
                    row=3, col=1
                )
                
                # RSI için yatay çizgiler (30 ve 70)
                for level in [30, 70]:
                    fig.add_hline(
                        y=level,
                        line_dash="dash",
                        line_color="gray",
                        opacity=0.5,
                        row=3, col=1
                    )

            # Grafik düzenini ayarla
            fig.update_layout(
                title=f'{symbol} Teknik Analiz Grafiği',
                title_x=0.5,
                **self.chart_config,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # X ekseni formatını ayarla
            fig.update_xaxes(
                rangeslider_visible=False,
                gridcolor=self.colors['grid']
            )

            # Y ekseni formatını ayarla
            fig.update_yaxes(
                gridcolor=self.colors['grid'],
                zerolinecolor=self.colors['grid']
            )

            # Son sinyalleri grafiğe ekle
            self.add_signals_to_chart(fig, symbol)

            self.charts[symbol] = fig
            self.last_update = datetime.now(pytz.UTC)
            return True

        except Exception as e:
            print(f"Grafik oluşturma hatası: {str(e)}")
            return False

    def calculate_rsi(self, prices, period=14):
        """RSI hesapla"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        except Exception as e:
            print(f"RSI hesaplama hatası: {str(e)}")
            return None

    def add_signals_to_chart(self, fig, symbol):
        """Sinyalleri grafiğe ekle"""
        try:
            # Son 24 saatteki sinyalleri al
            recent_signals = [s for s in self.signals 
                            if s['symbol'] == symbol and 
                            (datetime.now(pytz.UTC) - s['timestamp']).total_seconds() < 86400]

            for signal in recent_signals:
                color = self.colors['buy'] if signal['type'] == 'BUY' else self.colors['sell']
                fig.add_annotation(
                    x=signal['timestamp'],
                    y=0,  # Y pozisyonu otomatik ayarlanacak
                    text=f"{signal['type']}\n{signal['confidence']}%",
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=color,
                    font=dict(
                        size=10,
                        color=color
                    ),
                    row=1, col=1
                )
        except Exception as e:
            print(f"Sinyal ekleme hatası: {str(e)}")

    def save_and_show_chart(self, symbol):
        """Grafiği kaydet ve göster"""
        try:
            if symbol in self.charts:
                # Grafik klasörünü kontrol et
                charts_dir = Path('charts')
                charts_dir.mkdir(exist_ok=True)
                
                # Grafik dosya adını oluştur
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = charts_dir / f'{symbol}_chart_{timestamp}.html'
                
                # Eski grafikleri temizle
                self.cleanup_old_charts(symbol)
                
                # Yeni grafiği kaydet
                self.charts[symbol].write_html(filename)
                print(f"Grafik kaydedildi: {filename}")
                return True
            return False
        except Exception as e:
            print(f"Grafik kaydetme hatası: {str(e)}")
            return False

    def cleanup_old_charts(self, symbol, keep_last=5):
        """Eski grafikleri temizle"""
        try:
            charts_dir = Path('charts')
            files = list(charts_dir.glob(f'{symbol}_chart_*.html'))
            
            # Dosyaları tarihe göre sırala
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Eski dosyaları sil
            for file in files[keep_last:]:
                file.unlink()
                print(f"Eski grafik silindi: {file}")
        except Exception as e:
            print(f"Grafik temizleme hatası: {str(e)}")

    def get_recent_signals(self, symbol=None, hours=24):
        """Son sinyalleri getir"""
        try:
            recent_signals = []
            cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=hours)
            
            for signal in self.signals:
                if signal['timestamp'] > cutoff_time:
                    if symbol is None or signal['symbol'] == symbol:
                        recent_signals.append(signal)
            
            return recent_signals
        except Exception as e:
            print(f"Sinyal getirme hatası: {str(e)}")
            return []

    def print_summary(self):
        """Özet bilgileri yazdır"""
        try:
            print("\n=== Trading Bot Özeti ===")
            print(f"Son güncelleme: {self.last_update}")
            print(f"Toplam sinyal sayısı: {len(self.signals)}")
            
            # Son 24 saatteki sinyalleri analiz et
            recent_signals = self.get_recent_signals()
            if recent_signals:
                print("\nSon 24 saat:")
                print(f"Sinyal sayısı: {len(recent_signals)}")
                
                # Sinyal türlerine göre sayıları hesapla
                buy_signals = sum(1 for s in recent_signals if s['type'] == 'BUY')
                sell_signals = sum(1 for s in recent_signals if s['type'] == 'SELL')
                
                print(f"Alım sinyalleri: {buy_signals}")
                print(f"Satım sinyalleri: {sell_signals}")
                
                # Ortalama güven seviyesi
                avg_confidence = sum(s['confidence'] for s in recent_signals) / len(recent_signals)
                print(f"Ortalama güven seviyesi: {avg_confidence:.2f}%")
                
                # Son sinyal detayları
                print("\nSon 5 sinyal:")
                for signal in recent_signals[-5:]:
                    print(f"{signal['timestamp']}: {signal['type']} {signal['symbol']} "
                          f"({signal['confidence']}%) - {signal['reason']}")
            else:
                print("\nSon 24 saatte sinyal yok")
                
        except Exception as e:
            print(f"Özet yazdırma hatası: {str(e)}")

    def create_performance_chart(self, symbol):
        """Performans grafiği oluştur"""
        try:
            recent_signals = self.get_recent_signals(symbol)
            if not recent_signals:
                return False
                
            # Sinyal verilerini DataFrame'e dönüştür
            df = pd.DataFrame(recent_signals)
            df['hour'] = df['timestamp'].dt.hour
            
            # Saatlik sinyal dağılımı
            fig = go.Figure()
            
            # Alım sinyalleri
            buy_signals = df[df['type'] == 'BUY']
            fig.add_trace(go.Bar(
                x=buy_signals['hour'],
                y=buy_signals['confidence'],
                name='Alım Sinyalleri',
                marker_color=self.colors['buy']
            ))
            
            # Satım sinyalleri
            sell_signals = df[df['type'] == 'SELL']
            fig.add_trace(go.Bar(
                x=sell_signals['hour'],
                y=sell_signals['confidence'],
                name='Satım Sinyalleri',
                marker_color=self.colors['sell']
            ))
            
            # Grafik düzeni
            fig.update_layout(
                title=f'{symbol} Sinyal Performansı (Son 24 Saat)',
                xaxis_title='Saat',
                yaxis_title='Güven Seviyesi (%)',
                **self.chart_config
            )
            
            # Grafiği kaydet
            charts_dir = Path('charts')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = charts_dir / f'{symbol}_performance_{timestamp}.html'
            fig.write_html(filename)
            
            return True
            
        except Exception as e:
            print(f"Performans grafiği oluşturma hatası: {str(e)}")
            return False
