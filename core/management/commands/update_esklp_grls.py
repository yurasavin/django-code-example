from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
import telebot

from ktru.utils import parse_esklp, parse_grls


class Command(BaseCommand):
    """
    Парсит справочники ГРЛС и КТРУ
    """
    help = 'Parse ESKLP and GRLS'

    @transaction.atomic()
    def handle(self, *args, **options):
        parse_esklp.parse_eis()
        self.stdout.write(self.style.SUCCESS('ESKLP parsed'))

        parse_grls.GRLSParser().main()
        self.stdout.write(self.style.SUCCESS('GRLS parsed'))

        bot = telebot.TeleBot(settings.TELEBOT_KEY)
        user_id = settings.TELEGRAM_USER_ID
        bot.send_message(user_id, 'ЕСКЛП и ГРЛС обновлены')
