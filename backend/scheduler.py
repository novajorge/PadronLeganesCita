from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import logging
import pytz

from database import SessionLocal, Usuario, CitaDisponibilidad
from scraper import ScraperCitaPrevia
from notifications import notificador

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Zona horaria española
tz = pytz.timezone('Europe/Madrid')

# Última vez que se encontró disponibilidad
ultima_disponibilidad = None


def get_next_check_interval():
    """Determina el intervalo de verificación basado en la hora actual"""
    now = datetime.now(tz)
    hora = now.hour

    # 8:00 a 15:00 = cada 30 minutos
    # Resto = cada 1 hora
    if 8 <= hora < 15:
        return 30  # minutos
    else:
        return 60  # minutos


def verificar_citas():
    """Función principal de verificación de citas"""
    global ultima_disponibilidad

    logger.info("=" * 50)
    logger.info(f"Iniciando verificación de citas a las {datetime.now(tz)}")
    logger.info("=" * 50)

    scraper = ScraperCitaPrevia()

    try:
        # Verificar disponibilidad
        resultado = scraper.verificar_todas_las_citas(dias_anticipacion=60)

        # Contar total de citas encontradas
        total_citas = 0
        todas_las_citas = []

        for unidad in resultado.get("unidades", []):
            citas = unidad.get("citas_encontradas", [])
            total_citas += len(citas)
            todas_las_citas.extend(citas)

        hay_citas = total_citas > 0

        # Guardar en base de datos
        db = SessionLocal()
        try:
            # Guardar cada cita encontrada
            for cita in todas_las_citas:
                registro = CitaDisponibilidad(
                    hay_citas=True,
                    detalles=f"{cita['fecha']} {cita['hora']} - {cita.get('unidad', 'Padrón')}",
                    checked_at=datetime.utcnow()
                )
                db.add(registro)

            # También guardar un registro resumen
            registro_resumen = CitaDisponibilidad(
                hay_citas=hay_citas,
                detalles=f"Total: {total_citas} citas en {len(resultado.get('unidades', []))} unidades",
                checked_at=datetime.utcnow()
            )
            db.add(registro_resumen)
            db.commit()
        finally:
            db.close()

        # Si hay citas y no se habían notificado antes, notificar a todos los usuarios
        if hay_citas and not ultima_disponibilidad:
            logger.info(f"¡{total_citas} citas detectadas! Notificando a usuarios...")
            notificar_todos_usuarios(resultado, todas_las_citas)
            ultima_disponibilidad = datetime.now(tz)
        elif not hay_citas:
            # Resetear si no hay citas
            ultima_disponibilidad = None

        logger.info(f"Total citas encontradas: {total_citas}")

    except Exception as e:
        logger.error(f"Error en verificación: {e}")
    finally:
        scraper.cerrar()


def notificar_todos_usuarios(resultado: dict, todas_las_citas: list):
    """Notifica a todos los usuarios activos"""
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).filter(Usuario.activo == True).all()

        logger.info(f"Notificando a {len(usuarios)} usuarios")

        for usuario in usuarios:
            try:
                usuario_dict = {
                    "email": usuario.email,
                    "telefono": usuario.telefono,
                    "telegram_chat_id": usuario.telegram_chat_id,
                    "notify_email": usuario.notify_email,
                    "notify_telegram": usuario.notify_telegram,
                    "notify_whatsapp": usuario.notify_whatsapp
                }

                hay_citas = len(todas_las_citas) > 0

                resultados = notificador.notificar_usuario(
                    usuario_dict,
                    hay_citas,
                    todas_las_citas
                )

                logger.info(f"Usuario {usuario.nombre}: {resultados}")

            except Exception as e:
                logger.error(f"Error notificando usuario {usuario.id}: {e}")

    finally:
        db.close()


class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=tz)

    def iniciar(self):
        """Inicia el scheduler"""
        logger.info("Iniciando scheduler...")

        # Programar verificación inicial
        self.verificar_y_reprogramar()

        # Arrancar scheduler
        self.scheduler.start()
        logger.info("Scheduler iniciado")

    def verificar_y_reprogramar(self):
        """Verifica y reprograma el trabajo basado en la hora"""
        # Eliminar trabajos existentes
        self.scheduler.remove_all_jobs()

        # Obtener intervalo actual
        intervalo = get_next_check_interval()

        logger.info(f"Programando verificación cada {intervalo} minutos")

        # Añadir trabajo
        self.scheduler.add_job(
            verificar_citas,
            'interval',
            minutes=intervalo,
            id='verificar_citas',
            next_run_time=datetime.now(tz)
        )

    def detener(self):
        """Detiene el scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler detenido")


# Instancia global
scheduler_manager = SchedulerManager()


def iniciar_scheduler():
    """Inicia el scheduler (para chiamar desde main)"""
    scheduler_manager.iniciar()


def detener_scheduler():
    """Detiene el scheduler"""
    scheduler_manager.detener()
