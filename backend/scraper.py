from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperCitaPrevia:
    def __init__(self):
        self.url = "https://intraweb.leganes.org/CitaPrevia/"
        self.driver = None

    def _init_driver(self):
        """Inicializa el driver de Chrome en modo headless"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.binary_location = "/usr/bin/chromium"

        service = Service(executable_path="/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def verificar_disponibilidad(self):
        """Verifica si hay citas disponibles para Padrón"""
        try:
            if not self.driver:
                self._init_driver()

            logger.info(f"Accediendo a {self.url}")
            self.driver.get(self.url)

            # Esperar a que cargue la página
            time.sleep(3)

            # Obtener el HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Buscar elementos relevantes
            # La estructura puede variar, buscaremos indicadores de disponibilidad
            resultados = {
                "hay_citas": False,
                "mensaje": "",
                "detalles": []
            }

            # Buscar por texto común en citas previas
            texto_pagina = soup.get_text().lower()

            # Buscar opciones de servicio (Padrón, Casa del Reloj)
            servicios = soup.find_all(['a', 'button', 'div', 'li'], class_=lambda x: x and ('servicio' in x.lower() or 'padrón' in x.lower() or 'cita' in x.lower()))

            for servicio in servicios:
                texto = servicio.get_text().strip()
                if texto and len(texto) > 3:
                    logger.info(f"Servicio encontrado: {texto}")

            # Buscar indicadores de disponibilidad/disponibilidad
            disponibilidad = soup.find_all(['div', 'span', 'p'], string=lambda x: x and 'disponible' in x.lower() if x else False)

            if disponibilidad:
                resultados["hay_citas"] = True
                for d in disponibilidad:
                    resultados["detalles"].append(d.get_text().strip())

            logger.info(f"Resultado: {resultados}")
            return resultados

        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {e}")
            return {
                "hay_citas": False,
                "mensaje": f"Error: {str(e)}",
                "detalles": []
            }
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def cerrar(self):
        """Cierra el driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


# Función para testing
if __name__ == "__main__":
    scraper = ScraperCitaPrevia()
    resultado = scraper.verificar_disponibilidad()
    print(f"Resultado: {resultado}")
