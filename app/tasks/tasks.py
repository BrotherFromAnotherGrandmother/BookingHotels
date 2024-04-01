from pathlib import Path
from PIL import Image
from pydantic import EmailStr
from app.tasks.celery_app import celery_worker as celery

from app.tasks.email_templates import create_booking_confirmation_template
from app.config import settings

import smtplib
from loguru import logger


@celery.task
def process_pic(
        path: str,
):
    """Цель: с помощью функции process_pic и процесса celery, мы можем в фоновом режиме обрабатывать задачи,
     которые требуют мощьности нашего компьютера, а не API и celery выполняет их в отдельном процессе, нежели API

     Проблемы: если celery накопит много задач, задачи будут выполняться одна за одной
     и это может привести к перегрузке память нашего компьютера"""

    image_path = Path(path)
    image = Image.open(image_path)

    image_resized_1000_500 = image.resize((1000, 500))
    image_resized_200_100 = image.resize((200, 100))

    image_resized_1000_500.save(f"app/static/images/resized_1000_500_{image_path.name}")
    image_resized_200_100.save(f"app/static/images/resized_200_100_{image_path.name}")


@celery.task
def send_booking_confirmation_email(
        booking: dict,
        email_to: EmailStr,
):
    msg_content = create_booking_confirmation_template(booking, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        print(settings.SMTP_USER, settings.SMTP_PASS)
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
    # logger.info(f"Successfully send email message to {email_to}")
