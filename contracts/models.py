from django.db import models
from django.urls import reverse

from core.cache import delete_reestr_cache


class Contract(models.Model):
    """
    Модель контракта. Содержит информацию о контракте, ссылается на
    заявку и закупку
    ~~~!ВАЖНО!~~~
    Поле price считается и изменяются, при изменении связанных
    экземпляров ContractPrice
    """

    tender = models.OneToOneField(
        'tenders.Tender',
        verbose_name='Закупка',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    num = models.CharField('Номер', max_length=50)
    date = models.DateField('Дата', db_index=True)
    price = models.DecimalField(
        'Сумма',
        max_digits=11,
        decimal_places=2,
        default=0,
        null=True,
    )
    specif = models.TextField('Спецификация')
    ticket = models.OneToOneField(
        'tickets.Ticket',
        verbose_name='Заявка',
        on_delete=models.CASCADE,
    )
    bg_choices = (
        (False, 'Нет'),
        (True, 'Да'),
    )
    bank_guar = models.BooleanField('Банковская гарантия', choices=bg_choices)
    pledge = models.DecimalField(
        'Сумма обеспечения',
        max_digits=11,
        decimal_places=2,
    )
    kontragent = models.CharField('Контрагент', max_length=100)
    part_of_ikz = models.PositiveSmallIntegerField(
        '27-29 разряды ИКЗ (без нулей)',
        null=True,
        blank=True,
    )
    other_ikz_part = models.ForeignKey(
        'PartOfIkz',
        verbose_name='Остальная часть ИКЗ',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'Контракт №{self.num} от {self.date.strftime("%d.%m.%Y")}'

    def save(self, *args, **kwargs):
        """Extend родительский метод. Удаляет кеш реестра"""
        super().save(*args, **kwargs)
        for limit in self.ticket.year.all():
            year = limit.year
            delete_reestr_cache(year)

    def get_absolute_url(self):
        return reverse('contracts:contract_detail', args=[self.id])

    def get_economy(self):
        """Считает экономию"""
        if not self.tender:
            return 0
        all_prices = self.contractprice_set.all()
        return sum((money.get_economy() for money in all_prices))

    def save_price(self):
        """
        Метод вызывается при создании, обновлении, удалении связанных
        ContractPrice. Обновляет информацию о цене контракта и если есть
        связанная закупка, вызывает подобную функцию у нее
        """
        all_prices = self.contractprice_set.all()
        self.price = sum((cp.get_money_with_change() for cp in all_prices))
        self.save()
        if self.tender:
            self.tender.save_price_and_economy()

    def delete(self, *args, **kwargs):
        """
        Extend родительский метод
        Удаляет кеш реестра
        """
        for limit in self.ticket.year.all():
            year = limit.year
            delete_reestr_cache(year)
        super().delete(*args, **kwargs)
        if self.tender:
            self.tender.save_price_and_economy()

    def get_eis_url(self):
        """
        Возвращает ссылку на контракт в ЕИС
        """
        url = (
            'https://zakupki.gov.ru/epz/contract/search/results.html?'
            f'searchString={self.tender.ikz}'
        )
        return url

    def get_ikz_ep_300(self):
        num_27_29 = f'{self.part_of_ikz}'.rjust(3, '0')
        num_27_29 = f'<b>{num_27_29}</b>'
        return self.other_ikz_part.num_1_27_and_30_36.format(num_27_29)


class ContractChange(models.Model):
    """
    Модель доп. соглашения, содержит информацию об изменении контракта
    """
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        verbose_name='Контракт',
    )
    num = models.CharField('Номер', blank=True, max_length=10)
    date = models.DateField('Дата')
    reasons = (
        ('1', 'Увеличение суммы'),
        ('-1', 'Уменьшение суммы'),
        ('some', 'Изменение условий'),
        ('cancell', 'Расторжение'),
    )
    reason = models.CharField(
        'Причина изменения',
        max_length=7,
        choices=reasons,
    )

    def __str__(self):
        return f'Доп. соглашение №{self.num} от {self.date}'

    def get_absolute_url(self):
        return reverse('contracts:contract_detail', args=[self.contract.id])

    def delete(self, *args, **kwargs):
        super(ContractChange, self).delete(*args, **kwargs)
        self.contract.save_price()


class ContractNum(models.Model):
    """
    Порядковый номер контракта для реестра (до 100 т.р. по 223-ФЗ)
    """
    num = models.SmallIntegerField('Номер')

    def __str__(self):
        return str(self.num)

    def increase_num(self, ticket, num):
        """Увеличивает порядковый номер"""
        if ticket.tender_type.use_default_num:
            if ticket.get_num() == num:
                self.num += 1
                self.save()


class PartOfIkz(models.Model):
    """
    Часть номера ИКЗ для единственного поставщика до 600
    """
    num_27_29 = models.PositiveIntegerField('27-29 разряды ИКЗ')
    num_1_27_and_30_36 = models.CharField('Остальная часть', max_length=36)
    year = models.PositiveIntegerField('Год')

    def __str__(self):
        num_27_29 = f'{self.num_27_29}'.rjust(3, '0')
        num_27_29 = f'<b>{num_27_29}</b>'
        return self.num_1_27_and_30_36.format(num_27_29)
