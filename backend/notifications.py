import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional
from twilio.rest import Client
from telegram import Bot
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Notificador:
    def __init__(self):
        # Configuración de email (se configurará desde variables de entorno)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@citapadronleganes.es")

        # Configuración de Twilio (SMS y WhatsApp)
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "")

        # Configuración de Telegram
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    def enviar_email(self, to_email: str, asunto: str, mensaje: str) -> bool:
        """Envía un email"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("Email no configurado - SMTP_USER/SMTP_PASSWORD no definidos")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = asunto

            msg.attach(MIMEText(mensaje, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email enviado a {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False

    def enviar_telegram(self, chat_id: str, mensaje: str) -> bool:
        """Envía un mensaje por Telegram"""
        if not self.telegram_token:
            logger.warning("Telegram no configurado - TELEGRAM_BOT_TOKEN no definido")
            return False

        try:
            bot = Bot(token=self.telegram_token)
            bot.send_message(chat_id=chat_id, text=mensaje, parse_mode='HTML')
            logger.info(f"Telegram enviado a chat_id {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Error enviando Telegram: {e}")
            return False

    def enviar_whatsapp(self, to_phone: str, mensaje: str) -> bool:
        """Envía un mensaje por WhatsApp usando Twilio"""
        if not self.twilio_sid or not self.twilio_token:
            logger.warning("WhatsApp no configurado - TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN no definidos")
            return False

        try:
            client = Client(self.twilio_sid, self.twilio_token)

            # Twilio requiere formato: whatsapp:+NÚMERO
            from_phone = f"whatsapp:{self.twilio_phone}"
            to_phone_formatted = f"whatsapp:{to_phone}" if not to_phone.startswith('whatsapp:') else to_phone

            message = client.messages.create(
                from_=from_phone,
                body=mensaje,
                to=to_phone_formatted
            )

            logger.info(f"WhatsApp enviado a {to_phone} - SID: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return False

    def enviar_sms(self, to_phone: str, mensaje: str) -> bool:
        """Envía un SMS usando Twilio"""
        if not self.twilio_sid or not self.twilio_token:
            logger.warning("SMS no configurado - TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN no definidos")
            return False

        try:
            client = Client(self.twilio_sid, self.twilio_token)

            message = client.messages.create(
                body=mensaje,
                from_=self.twilio_phone,
                to=to_phone
            )

            logger.info(f"SMS enviado a {to_phone} - SID: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")
            return False

    def notificar_usuario(self, usuario: dict, hay_citas: bool, detalles: list) -> dict:
        """Notifica a un usuario por todos los canales activos"""
        if hay_citas:
            asunto = "🚨 ¡Citas disponibles! - Padrón Leganés"
            mensaje = self._generar_mensaje_citas(detalles)
        else:
            return {"status": "no_hay_citas", "enviados": 0}

        resultados = {
            "email": False,
            "telegram": False,
            "whatsapp": False
        }

        # Email
        if usuario.get("notify_email") and usuario.get("email"):
            resultados["email"] = self.enviar_email(
                usuario["email"],
                asunto,
                mensaje
            )

        # Telegram
        if usuario.get("notify_telegram") and usuario.get("telegram_chat_id"):
            resultados["telegram"] = self.enviar_telegram(
                usuario["telegram_chat_id"],
                mensaje
            )

        # WhatsApp
        if usuario.get("notify_whatsapp") and usuario.get("telefono"):
            resultados["whatsapp"] = self.enviar_whatsapp(
                usuario["telefono"],
                mensaje.replace("<b>", "").replace("</b>", "")
            )

        return resultados

    def _generar_mensaje_citas(self, detalles: list) -> str:
        """Genera el mensaje de notificación de citas"""
        mensaje = """
        <html>
        <body>
            <h2 style="color: #1e40af;">🚨 ¡Citas Disponibles!</h2>
            <p>Se han detectado citas disponibles para <b>Padrón</b> en la Casa del Reloj de Leganés.</p>
        """

        if detalles:
            mensaje += "<h3>Detalles:</h3><ul>"
            for d in detalles:
                mensaje += f"<li>{d}</li>"
            mensaje += "</ul>"

        mensaje += """
            <p>Accede ahora: <a href="https://intraweb.leganes.org/CitaPrevia/">Cita Previa Leganés</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Servicio de monitorización de citas - No respondas a este mensaje.
            </p>
        </body>
        </html>
        """
        return mensaje


# Notificador singleton
notificador = Notificador()
