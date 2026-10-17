"""Envío de correos por SMTP (MailHog en desarrollo)."""
import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings

log = logging.getLogger(__name__)


def enviar(destino: str, asunto: str, cuerpo: str) -> bool:
    s = get_settings()
    mensaje = EmailMessage()
    mensaje["From"], mensaje["To"], mensaje["Subject"] = s.smtp_remitente, destino, asunto
    mensaje.set_content(cuerpo)
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=10) as smtp:
            smtp.send_message(mensaje)
        return True
    except (OSError, smtplib.SMTPException) as e:
        log.warning("No se pudo enviar el correo a %s: %s", destino, e)
        return False
