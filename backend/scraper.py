from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperCitaPrevia:
    """Scraper para verificar disponibilidad de citas del Padrón en Leganés"""

    URL_BASE = "https://intraweb.leganes.org/CitaPrevia/"
    SERVICIO_PADRON = "35"

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
        """Inicializa el driver de Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.binary_location = "/usr/bin/google-chrome"

        service = Service(executable_path="/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def _seleccionar_servicio_y_unidad(self, unidad_value: str) -> bool:
        """Selecciona el servicio de Padrón y la unidad"""
        try:
            logger.info("Esperando a que cargue la página...")

            # Esperar a que aparezcan los selects
            self.wait.until(EC.presence_of_element_located((By.ID, "select-service")))
            time.sleep(2)

            # Seleccionar servicio
            select_servicio = self.driver.find_element(By.ID, "select-service")
            Select(select_servicio).select_by_value(self.SERVICIO_PADRON)
            logger.info("Servicio seleccionado: SAC - Casa del Reloj Mañanas - Padrón")
            time.sleep(2)

            # Seleccionar unidad
            select_unidad = self.driver.find_element(By.ID, "select-provider")
            Select(select_unidad).select_by_value(unidad_value)
            logger.info(f"Unidad seleccionada: {unidad_value}")
            time.sleep(2)

            # Click en Siguiente
            boton = self.driver.find_element(By.ID, "button-next-1")
            boton.click()
            logger.info("Clicked en Siguiente, esperando calendario...")
            time.sleep(5)

            return True

        except Exception as e:
            logger.error(f"Error al seleccionar servicio/unidad: {e}")
            self._guardar_html_debug()
            return False

    def _obtener_mes_actual(self) -> tuple:
        """Obtiene el mes y año actuales del calendario"""
        try:
            mes_element = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-month")
            ano_element = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-year")

            mes_texto = mes_element.text.strip()
            ano_texto = ano_element.text.strip()

            meses = {
                "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
                "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
                "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
            }

            return (meses.get(mes_texto, 1), int(ano_texto))
        except Exception as e:
            logger.error(f"Error al obtener mes: {e}")
            return (datetime.now().month, datetime.now().year)

    def _navegar_mes(self, mes_objetivo: int, ano_objetivo: int):
        """Navega al mes objetivo"""
        try:
            clicks = 0
            while True:
                mes_actual, ano_actual = self._obtener_mes_actual()
                logger.info(f"Mes actual: {mes_actual}/{ano_actual}, Objetivo: {mes_objetivo}/{ano_objetivo}")

                if (ano_actual > ano_objetivo) or (ano_actual == ano_objetivo and mes_actual >= mes_objetivo):
                    break

                btn = self.driver.find_element(By.CSS_SELECTOR, "a.ui-datepicker-next")
                btn.click()
                time.sleep(1.5)
                clicks += 1

                if clicks > 12:
                    logger.warning("Demasiados clicks, saliendo")
                    break

            logger.info(f"Navegación completada tras {clicks} clicks")
        except Exception as e:
            logger.error(f"Error navegando meses: {e}")

    def _obtener_dias_disponibles(self) -> list:
        """Obtiene los días con citas disponibles"""
        dias = []
        mes_actual, ano_actual = self._obtener_mes_actual()

        try:
            # Buscar todas las celdas de días clickeables
            celdas = self.driver.find_elements(By.CSS_SELECTOR, "td[data-handler='selectDay']")
            logger.info(f"Encontradas {len(celdas)} celdas de días")

            for celda in celdas:
                try:
                    # Verificar si es un día válido (tiene link)
                    link = celda.find_element(By.CSS_SELECTOR, "a.ui-state-default")
                    dia_texto = link.text.strip()

                    if not dia_texto:
                        continue

                    dia_num = int(dia_texto)

                    # Click en el día para ver las horas
                    link.click()
                    time.sleep(2)  # Esperar a que carguen las horas

                    # Buscar horas disponibles
                    horas_container = self.driver.find_element(By.ID, "available-hours")
                    horas_spans = horas_container.find_elements(By.CSS_SELECTOR, "span.available-hour")

                    if horas_spans:
                        horas = [h.text.strip() for h in horas_spans if h.text.strip()]
                        if horas:
                            logger.info(f"Día {dia_num}: {len(horas)} horas disponibles")
                            dias.append({
                                "dia": dia_num,
                                "mes": mes_actual,
                                "ano": ano_actual,
                                "horas": horas
                            })

                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.error(f"Error procesando día: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error al obtener días: {e}")

        return dias

    def _guardar_html_debug(self):
        """Guarda HTML para debug"""
        try:
            filename = f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info(f"Guardado debug en {filename}")
        except:
            pass

    def verificar_citas_unidad(self, unidad_nombre: str, unidad_value: str, dias_anticipacion: int = 60) -> dict:
        """Verifica citas para una unidad"""
        resultado = {
            "unidad": unidad_nombre,
            "unidad_id": unidad_value,
            "citas_encontradas": [],
            "error": None
        }

        try:
            self.driver.get(self.URL_BASE)
            time.sleep(5)

            if not self._seleccionar_servicio_y_unidad(unidad_value):
                resultado["error"] = "Error al seleccionar servicio"
                return resultado

            # Calcular mes objetivo
            fecha_actual = datetime.now()
            fecha_objetivo = fecha_actual + timedelta(days=dias_anticipacion)

            # Navegar al mes
            self._navegar_mes(fecha_objetivo.month, fecha_objetivo.year)

            # Obtener días
            dias = self._obtener_dias_disponibles()

            for dia_info in dias:
                for hora in dia_info["horas"]:
                    resultado["citas_encontradas"].append({
                        "fecha": f"{dia_info['dia']}/{dia_info['mes']}/{dia_info['ano']}",
                        "hora": hora,
                        "unidad": unidad_nombre
                    })

            logger.info(f"{unidad_nombre}: {len(resultado['citas_encontradas'])} citas")

        except Exception as e:
            logger.error(f"Error verificando {unidad_nombre}: {e}")
            resultado["error"] = str(e)

        return resultado

    def verificar_todas_las_citas(self, dias_anticipacion: int = 60) -> dict:
        """Verifica todas las unidades"""
        resultado = {
            "fecha_verificacion": datetime.now().isoformat(),
            "unidades": []
        }

        try:
            if not self.driver:
                self._init_driver()

            for nombre, valor in self.UNIDADES.items():
                logger.info(f"=== Verificando {nombre} ===")
                res = self.verificar_citas_unidad(nombre, valor, dias_anticipacion)
                resultado["unidades"].append(res)
                time.sleep(3)

        except Exception as e:
            logger.error(f"Error: {e}")
            resultado["error"] = str(e)

        return resultado

    def verificar_disponibilidad(self):
        return self.verificar_todas_las_citas()

    def cerrar(self):
        if self.driver:
            self.driver.quit()
            self.driver = None


if __name__ == "__main__":
    scraper = ScraperCitaPrevia()
    try:
        resultado = scraper.verificar_todas_las_citas()
        print(f"\n=== RESULTADO ===")
        print(f"Fecha: {resultado['fecha_verificacion']}")

        total = 0
        for u in resultado["unidades"]:
            print(f"\n{u['unidad']}:")
            if u.get("error"):
                print(f"  ERROR: {u['error']}")
            else:
                print(f"  Citas: {len(u['citas_encontradas'])}")
                total += len(u['citas_encontradas'])
                for c in u['citas_encontradas'][:3]:
                    print(f"    - {c['fecha']} {c['hora']}")

        print(f"\nTotal: {total} citas")
    finally:
        scraper.cerrar()
