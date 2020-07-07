import os

import requests

import telebot

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings

from ktru.models import Coronavirus

logger = get_task_logger(__name__)


@shared_task(name='send_message_to_telegram')
def send_message_to_telegram(message: str):
    """
    Отправляет сообщение в админский канал
    """
    bot = telebot.TeleBot(settings.TELEBOT_KEY)
    user_id = settings.TELEGRAM_USER_ID
    bot.send_message(user_id, message, parse_mode='HTML')


@shared_task(name='make_backup')
def make_backup():
    db_url = os.environ['DATABASE_URL']

    backup_path = settings.PATH_TO_BACKUP
    command = f"pg_dump -f {backup_path} --dbname={db_url} -Fc --clean"
    os.system(command)
    logger.info('[make_backup] backup created succesful')
    send_backup.delay()


@shared_task(name='send_backup')
def send_backup():
    bot = telebot.TeleBot(settings.TELEBOT_KEY)
    user_id = settings.TELEGRAM_USER_ID

    file_path = settings.PATH_TO_BACKUP
    with open(file_path, 'rb') as doc:
        bot.send_document(user_id, doc)
    os.remove(file_path)
    logger.info('[send_backup] Backup sended succesful')
