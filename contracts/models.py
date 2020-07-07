from django.db import models


class Contract(models.Model):

    tender = models.OneToOneField('tenders.Tender', blank=True, null=True,
                                  on_delete=models.CASCADE)
    num = models.CharField(max_length=50)
    date = models.DateField(db_index=True)
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0,
                                null=True)
    specif = models.TextField()
    ticket = models.OneToOneField('tickets.Ticket', on_delete=models.CASCADE)
    bank_guar = models.BooleanField()
    pledge = models.DecimalField(max_digits=11, decimal_places=2)
    kontragent = models.CharField(max_length=100)

    def __str__(self):
        return f'Контракт №{self.num} от {self.date.strftime("%d.%m.%Y")}'


class ContractChange(models.Model):

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    num = models.CharField('Номер', blank=True, max_length=10)
    date = models.DateField('Дата')

    def __str__(self):
        return f'Доп. соглашение №{self.num} от {self.date}'
