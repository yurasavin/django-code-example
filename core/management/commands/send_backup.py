import os
import telebot

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Отправляет готовые бекапы через бота и очищает директорию с ними на диске
    """
    help = 'Send backups to telegram and remove them from disk'

    def handle(self, *args, **options):
        bot = telebot.TeleBot(settings.TELEBOT_KEY)
        user_id = settings.TELEGRAM_USER_ID

        os.chdir(settings.PATH_TO_BACKUP)
        files = [f for f in os.listdir()]
        for file_name in files:
            file_path = os.path.join(os.path.curdir, file_name)
            with open(file_path, 'rb') as doc:
                bot.send_document(user_id, doc)
            os.remove(file_path)
        self.stdout.write(self.style.SUCCESS('Backup sended succesful'))
