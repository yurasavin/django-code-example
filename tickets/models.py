from django.db import models
from django.urls import reverse

from contracts.models import ContractNum


class Ticket(models.Model):

    name = models.CharField('Предмет закупки', max_length=100)
    date = models.DateField('Дата получения', auto_now_add=True, db_index=True)

    status = models.BooleanField(
        "Статус",
        max_length=10,
        default=True
    )
    year = models.ManyToManyField(
        'limits.Limit',
        verbose_name='Годы лимитов',
        db_index=True,
    )

    def __str__(self):
        return self.name
