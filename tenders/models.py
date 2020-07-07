from django.db import models
from django.db.models import Sum


class Tender(models.Model):

    ikz = models.CharField(max_length=36, blank=True)
    num = models.CharField(max_length=19, unique=True)
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    economy = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    statuses = (
        ('in_work', 'In work'),
        ('done', 'Done'),
        ('zero', 'Zero'),
        ('cancel', 'Cancelled'),
    )
    status = models.CharField(max_length=20, blank=True, choices=statuses,
                              default=statuses[0][0], db_index=True)
    smp = models.BooleanField()
    ticket = models.OneToOneField('tickets.Ticket', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.num}; {self.price}'
