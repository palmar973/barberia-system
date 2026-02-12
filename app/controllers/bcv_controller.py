import sys
import re
import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QThread, Signal
import urllib3

# Desactivar advertencias de SSL inseguro (necesario para BCV)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def obtener_tasa():
    """Obtiene la tasa USD del BCV con parsing tolerante a cambios de HTML."""
    url = "https://www.bcv.org.ve/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1) Estructura clásica BCV
        candidatos = [
            soup.select_one('div#dolar strong'),
            soup.select_one('#dolar strong'),
            soup.select_one('div#dolar span'),
            soup.select_one('#dolar'),
            soup.select_one('div[id*="dolar" i] strong'),
            soup.select_one('div[id*="dolar" i] span'),
            soup.select_one('div[id*="dolar" i]'),
        ]

        texto_tasa = None
        for nodo in candidatos:
            if nodo:
                valor = nodo.get_text(" ", strip=True)
                if valor:
                    texto_tasa = valor
                    break

        # 2) Fallback: buscar cualquier patrón numérico tipo "xx,xxxx"
        if not texto_tasa:
            match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d+|\d+,\d+|\d+\.\d+)', soup.get_text(" ", strip=True))
            if match:
                texto_tasa = match.group(1)

        if not texto_tasa:
            raise ValueError("No se encontró el precio del dólar en el HTML del BCV")

        # Limpiar texto: quitar Bs/espacios y normalizar decimal
        tasa_limpia = texto_tasa
        tasa_limpia = tasa_limpia.replace('Bs.', '').replace('Bs', '').replace('VES', '')
        tasa_limpia = tasa_limpia.replace('\xa0', '').replace(' ', '').strip()

        if ',' in tasa_limpia and '.' in tasa_limpia:
            tasa_limpia = tasa_limpia.replace('.', '').replace(',', '.')
        else:
            tasa_limpia = tasa_limpia.replace(',', '.')

        match_num = re.search(r'\d+(?:\.\d+)?', tasa_limpia)
        if not match_num:
            raise ValueError(f"Formato de tasa inválido: {texto_tasa}")

        return float(match_num.group(0))

    except Exception as e:
        print(f"[BCV] Error real al obtener tasa: {e}")
        raise

class BCVWorker(QThread):
    """Hilo de scraping del BCV sin congelar la UI."""
    precio_actualizado = Signal(float)
    error_ocurrido = Signal(str)

    def run(self):
        try:
            tasa = obtener_tasa()
            self.precio_actualizado.emit(tasa)
        except Exception as e:
            self.error_ocurrido.emit(f"Fallo conexión: {str(e)}")