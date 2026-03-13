from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperCitaPrevia:
    """Scraper para verificar disponibilidad de citas del Padrón en Leganés"""

    # Constantes del servicio
    URL_BASE = "https://intraweb.leganes.org/CitaPrevia/"
    SERVICIO_PADRON = "35"  # SAC - Casa del Reloj Mañanas - Padrón

    # Unidades de Padrón
    UNIDADES = {
        "Padrón 1": "58735",
        "Padrón 3": "58737",
        "Padrón 4": "58738",
        "Padrón 5": "58742"
    }

    def __init__(self):
        self.driver = None
        self.wait = None

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
        chrome_options.binary_location = "/usr/bin/google-chrome"

        service = Service(executable_path="/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

    def _seleccionar_servicio_y_unidad(self, unidad_value: str) -> bool:
        """Selecciona el servicio de Padrón y la unidad específica"""
        try:
            # Seleccionar servicio (value=35 = SAC - Casa del Reloj Mañanas - Padrón)
            select_servicio = self.wait.until(
                EC.presence_of_element_located((By.ID, "select-service"))
            )
            Select(select_servicio).select_by_value(self.SERVICIO_PADRON)
            logger.info("Servicio seleccionado: SAC - Casa del Reloj Mañanas - Padrón")
            time.sleep(1)

            # Seleccionar unidad (Padrón 1, 3, 4, o 5)
            select_unidad = self.wait.until(
                EC.presence_of_element_located((By.ID, "select-provider"))
            )
            Select(select_unidad).select_by_value(unidad_value)
            logger.info(f"Unidad seleccionada: {unidad_value}")
            time.sleep(1)

            # Hacer clic en Siguiente para avanzar al paso 2 (calendario)
            boton_siguiente = self.wait.until(
                EC.element_to_be_clickable((By.ID, "button-next-1"))
            )
            boton_siguiente.click()
            time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Error al seleccionar servicio/unidad: {e}")
            return False

    def _obtener_mes_actual(self) -> tuple:
        """Obtiene el mes y año actuales del calendario"""
        try:
            mes_element = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-month")
            ano_element = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-year")

            mes_texto = mes_element.text.strip()
            ano_texto = ano_element.text.strip()

            # Convertir mes en español a número
            meses = {
                "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
                "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
                "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
            }

            mes_num = meses.get(mes_texto, 1)
            ano_num = int(ano_texto)

            return (mes_num, ano_num)
        except Exception as e:
            logger.error(f"Error al obtener mes actual: {e}")
            return (datetime.now().month, datetime.now().year)

    def _navegar_mes(self, mes_objetivo: int, ano_objetivo: int) -> bool:
        """Navega al mes objetivo clicking en el botón Siguiente"""
        try:
            while True:
                mes_actual, ano_actual = self._obtener_mes_actual()

                # Si ya estamos en el mes objetivo, salir
                if (ano_actual, mes_actual) >= (ano_objetivo, mes_objetivo):
                    break

                # Click en siguiente mes
                btn_siguiente = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "a.ui-datepicker-next[data-handler='next']"
                )
                btn_siguiente.click()
                time.sleep(1)

            return True
        except Exception as e:
            logger.error(f"Error al navegar al mes: {e}")
            return False

    def _obtener_dias_disponibles(self) -> list:
        """Obtiene los días del mes actual que tienen citas disponibles"""
        dias_disponibles = []

        try:
            # Buscar celdas de días en el calendario
            celdas_dias = self.driver.find_elements(
                By.CSS_SELECTOR,
                "td[data-handler='selectDay']"
            )

            for celda in celdas_dias:
                try:
                    # Verificar si el día tiene disponibilidad
                    # Los días sin disponibilidad pueden tener una clase diferente o no tener horas
                    link = celda.find_element(By.CSS_SELECTOR, "a")
                    dia = link.text.strip()

                    if dia:
                        # Click en el día para ver las horas disponibles
                        link.click()
                        time.sleep(1)

                        # Buscar horas disponibles
                        horas = self.driver.find_elements(
                            By.CSS_SELECTOR,
                            "span.available-hour"
                        )

                        if horas:
                            horas_disponibles = [h.text.strip() for h in horas]
                            dias_disponibles.append({
                                "dia": dia,
                                "horas": horas_disponibles
                            })
                            logger.info(f"Día {dia}: {len(horas_disponibles)} horas disponibles")

                except NoSuchElementException:
                    # No hay horas disponibles para este día
                    continue

        except Exception as e:
            logger.error(f"Error al obtener días disponibles: {e}")

        return dias_disponibles

    def verificar_citas_unidad(self, unidad_nombre: str, unidad_value: str, dias_anticipacion: int = 60) -> dict:
        """Verifica citas disponibles para una unidad específica en los próximos N días"""
        resultado = {
            "unidad": unidad_nombre,
            "unidad_id": unidad_value,
            "citas_encontradas": [],
            "fecha_verificacion": datetime.now().isoformat(),
            "error": None
        }

        try:
            # Navegar a la página principal
            self.driver.get(self.URL_BASE)
            time.sleep(3)

            # Seleccionar servicio y unidad
            if not self._seleccionar_servicio_y_unidad(unidad_value):
                resultado["error"] = "Error al seleccionar servicio/unidad"
                return resultado

            # Obtener fecha actual y fecha objetivo
            fecha_actual = datetime.now()
            fecha_objetivo = fecha_actual + timedelta(days=dias_anticipacion)

            # Mes objetivo
            mes_objetivo = fecha_objetivo.month
            ano_objetivo = fecha_objetivo.year

            # Navegar al mes objetivo
            self._navegar_mes(mes_objetivo, ano_objetivo)

            # Obtener días con disponibilidad
            dias = self._obtener_dias_disponibles()

            # Obtener mes/año actual para crear fechas completas
            mes_actual, ano_actual = self._obtener_mes_actual()

            for dia_info in dias:
                dia = dia_info["dia"]
                horas = dia_info["horas"]

                for hora in horas:
                    resultado["citas_encontradas"].append({
                        "fecha": f"{dia}/{mes_actual}/{ano_actual}",
                        "hora": hora,
                        "datetime": f"{ano_actual}-{mes_actual:02d}-{int(dia):02d} {hora}:00"
                    })

            logger.info(f"{unidad_nombre}: {len(resultado['citas_encontradas'])} citas encontradas")

        except Exception as e:
            logger.error(f"Error al verificar citas para {unidad_nombre}: {e}")
            resultado["error"] = str(e)

        return resultado

    def verificar_todas_las_citas(self, dias_anticipacion: int = 60) -> dict:
        """Verifica citas disponibles para todas las unidades de Padrón"""
        resultado_final = {
            "fecha_verificacion": datetime.now().isoformat(),
            "dias_anticipacion": dias_anticipacion,
            "unidades": []
        }

        try:
            if not self.driver:
                self._init_driver()

            for unidad_nombre, unidad_value in self.UNIDADES.items():
                logger.info(f"Verificando citas para {unidad_nombre}...")

                resultado = self.verificar_citas_unidad(
                    unidad_nombre,
                    unidad_value,
                    dias_anticipacion
                )
                resultado_final["unidades"].append(resultado)

                # Reiniciar para la siguiente unidad
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error al verificar todas las citas: {e}")
            resultado_final["error"] = str(e)

        return resultado_final

    def verificar_disponibilidad(self) -> dict:
        """Método de compatibilidad con la versión anterior"""
        return self.verificar_todas_las_citas()

    def cerrar(self):
        """Cierra el driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


# Función para testing
if __name__ == "__main__":
    scraper = ScraperCitaPrevia()
    try:
        resultado = scraper.verificar_todas_las_citas()
        print(f"\n=== RESULTADO ===")
        print(f"Fecha verificación: {resultado['fecha_verificacion']}")
        for unidad in resultado["unidades"]:
            print(f"\n{unidad['unidad']} ({unidad['unidad_id']}):")
            if unidad["error"]:
                print(f"  Error: {unidad['error']}")
            else:
                print(f"  Citas encontradas: {len(unidad['citas_encontradas'])}")
                for cita in unidad["citas_encontradas"][:5]:  # Mostrar solo las primeras 5
                    print(f"    - {cita['fecha']} {cita['hora']}")
                if len(unidad["citas_encontradas"]) > 5:
                    print(f"    ... y {len(unidad['citas_encontradas']) - 5} más")
    finally:
        scraper.cerrar()
