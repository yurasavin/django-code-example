from django.db import models
from django.db.models import Sum
from django.urls import reverse

from core.cache import delete_reestr_cache

DOMAIN = 'https://zakupki.gov.ru'


class Tender(models.Model):
    """
    Модель закупки. Содержит информацию о закупке, ссылается на заявку.

    ~~~!ВАЖНО!~~~
    Поля price и economy считаются и изменяются сами, при изменении связанных
    экземпляров StartPrice и связанных с ними ContractPrice
    """

    ikz = models.CharField('ИКЗ', max_length=36, blank=True)
    num = models.CharField(
        "Номер извещения",
        max_length=19,
        unique=True,
    )
    price = models.DecimalField(
        'НМЦК',
        max_digits=11,
        decimal_places=2,
        default=0,
    )
    economy = models.DecimalField(
        'Экономия',
        max_digits=11,
        decimal_places=2,
        default=0,
    )
    statuses = (
        ('in_work', 'Закупка осуществляется'),
        ('done', 'Закупка завершена'),
        ('zero', 'Закупка не состоялась'),
        ('cancel', 'Закупка отменена'),
    )
    status = models.CharField(
        "Статус закупки",
        max_length=20,
        blank=True,
        choices=statuses,
        default=statuses[0][0],
        db_index=True)
    smp_choices = (
        (True, 'Да'),
        (False, 'Нет'),
    )
    smp = models.BooleanField("Закупка для СМП", choices=smp_choices)
    ticket = models.OneToOneField(
        'tickets.Ticket',
        verbose_name='Заявка',
        on_delete=models.CASCADE,
    )

    @property
    def first_page_url(self):
        raw_url = '{}/epz/order/notice/ea44/view/common-info.html?regNumber={}'
        return raw_url.format(DOMAIN, self.num)

    @property
    def second_page_url(self):
        raw_url = '{}/epz/order/notice/ea44/view/documents.html?regNumber={}'
        return raw_url.format(DOMAIN, self.num)

    @property
    def third_page_url(self):
        raw_url = (
            '{}/epz/order/notice/ea44/view/supplier-results.html?regNumber={}'
        )
        return raw_url.format(DOMAIN, self.num)

    @property
    def search_results_url(self):
        raw_url = '{}/epz/order/notice/rpec/search-results.html?orderNum={}'
        return raw_url.format(DOMAIN, self.num)

    def __str__(self):
        return f'{self.num}; {self.price}'

    def save(self, *args, **kwargs):
        """
        Extend родительский метод
        Удаляет кеш реестра
        """
        super().save(*args, **kwargs)
        for limit in self.ticket.year.all():
            year = limit.year
            delete_reestr_cache(year)

    def delete(self, *args, **kwargs):
        """
        Extend родительский метод
        Удаляет кеш реестра
        """
        for limit in self.ticket.year.all():
            year = limit.year
            delete_reestr_cache(year)
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tenders:tender_detail', args=[self.id])

    def print_smp(self):
        """Возвращает ответ на вопрос, проводится ли закупка для СМП"""
        return 'Да' if self.smp else 'Нет'

    def save_price_and_economy(self):
        """
        Метод вызывается при создании, обновлении, удалении связанных
        StartPrice/ContractPrice. Обновляет информацию о начальной цене
        закупки и экономии
        """
        self.price = self.startprice_set.all().aggregate(m=Sum('money'))['m']
        self.price = self.price if self.price else 0
        if hasattr(self, 'contract'):
            contract_price = self.contract.contractprice_set.aggregate(
                money=Sum('money'))['money'] or 0
            self.economy = self.price - contract_price
        else:
            self.economy = 0
        self.save()

    @classmethod
    def get_fields_for_view(cls, law):
        """Возвращает поля для формы"""
        if law == 44:
            fields = ['ikz', 'num', 'status', 'smp']
        elif law == 223:
            fields = ['num', 'status']
        return fields


class TenderType(models.Model):
    name = models.CharField('Способ закупки', max_length=30)
    laws = (
        (223, '223-ФЗ'),
        (44, '44-ФЗ'),
    )
    law = models.SmallIntegerField('Закон', choices=laws, db_index=True)
    need_publicate = models.BooleanField('Нужно публиковать')
    use_default_num = models.BooleanField('Генерировать номер')
    ep_and_use_ikz = models.BooleanField(
        'Генерировать часть ИКЗ (ЕП до 600)',
        default=False,
    )
    buy_from_singe_supplier = models.BooleanField(
        'Закупка у единственного поставщика',
    )

    def __str__(self):
        return f'{self.name} {self.get_law_display()}'

    def dont_need_bank_guar(self):
        """Возвращает True, если для способа не нужна банковская гарантия"""
        if self.law == 44 and self.need_publicate:
            return False
        return True
