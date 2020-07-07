import os
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Делает бекап базы данных в форматах json и sql"""
    help = 'Make database backup to json and sql. Send this to telegram'

    def handle(self, *args, **options):
        date = datetime.date.today().strftime("%d.%m.%Y")
        db = settings.DATABASES['default']
        user = db['USER']
        bd_name = db['NAME']
        db_passw = db['PASSWORD']
        db_port = db['PORT']

        # Делаем бекап базы данных в sql
        command = f"pg_dump -f {settings.PATH_TO_BACKUP}/backup.dump --dbname=postgres://{user}:{db_passw}@postgres:{db_port}/{bd_name} -Fc"
        os.system(command)

        self.stdout.write(self.style.SUCCESS('Backup written succesful'))
