import sys
import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QThread, Signal
import urllib3

# Desactivar advertencias de SSL inseguro (necesario para BCV)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BCVWorker(QThread):
    """Hilo de scraping del BCV sin congelar la UI."""
    precio_actualizado = Signal(float)
    error_ocurrido = Signal(str)

    def run(self):
        url = "http://www.bcv.org.ve/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                dolar_div = soup.find('div', id='dolar')
                
                if dolar_div:
                    rate_text = dolar_div.find('strong').text.strip()
                    # Convierto formato europeo (35,1234) a float
                    rate_clean = rate_text.replace(',', '.')
                    rate_float = float(rate_clean)
                    
                    self.precio_actualizado.emit(rate_float)
                else:
                    self.error_ocurrido.emit("No se encontró el selector #dolar")
            else:
                self.error_ocurrido.emit(f"Error HTTP {response.status_code}")
                
        except Exception as e:
            self.error_ocurrido.emit(f"Fallo conexión: {str(e)}")