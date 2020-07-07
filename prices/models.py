from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse

from core.cache import delete_reestr_cache


class AbstractPrice(models.Model):
    """Абстрактная модель цены"""

    class Meta:
        abstract = True

    money = models.DecimalField('Сумма', max_digits=11, decimal_places=2)
    limit = models.ForeignKey(
        'limits.LimitMoney',
        on_delete=models.CASCADE,
        verbose_name='Лимиты',
    )
    subdivision = models.ForeignKey(
        'limits.Subdivision',
        verbose_name='Подраздел',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Сумма: {self.money}'


class StartPrice(AbstractPrice):
    """Модель начальной цены закупки"""

    tender = models.ForeignKey(
        'tenders.Tender',
        verbose_name='Закупка',
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        """
        Extend родительский метод
        При сохранении вызывает метод связанного Tender
        Удаляет кеш лимитов и реестра
        """
        super().save(*args, **kwargs)
        year = self.limit.industry_code.limit_article.source.limit.year
        delete_reestr_cache(year)
        if hasattr(self, 'contractprice'):
            changed = False
            if self.contractprice.limit != self.limit:
                self.contractprice.limit = self.limit
                changed = True
            if self.contractprice.subdivision != self.subdivision:
                self.contractprice.subdivision = self.subdivision
                changed = True
            if changed:
                self.contractprice.save()
        elif hasattr(self.tender, 'contract'):
            self.tender.contract.contractprice_set.create(
                start_price=self,
                money=0,
                limit=self.limit,
                subdivision=self.subdivision,
            )
            self.contractprice.save()
        self.tender.save_price_and_economy()

    def delete(self, *args, **kwargs):
        """
        Extend родительский метод
        При удалении вызывает метод связанного Tender
        Удаляет кеш лимитов и реестра
        """
        year = self.limit.industry_code.limit_article.source.limit.year
        delete_reestr_cache(year)
        super().delete(*args, **kwargs)
        self.tender.save_price_and_economy()

    def get_absolute_url(self):
        """Возвращает ссылку на связанный Tender"""
        return reverse('tenders:tender_detail', args=[self.tender.id])


class ContractPrice(AbstractPrice):
    """Модель цены контракта"""

    start_price = models.OneToOneField(
        StartPrice,
        verbose_name='НМЦК',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    contract = models.ForeignKey(
        'contracts.Contract',
        verbose_name='Контракт',
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        """
        Extend родительский метод
        При сохранении вызывает метод связанного Contract и StartPrice
        """
        super().save(*args, **kwargs)
        year = self.limit.industry_code.limit_article.source.limit.year
        delete_reestr_cache(year)
        if self.start_price:
            changed = False
            if self.start_price.limit != self.limit:
                self.start_price.limit = self.limit
                changed = True
            if self.start_price.subdivision != self.subdivision:
                self.start_price.subdivision = self.subdivision
                changed = True
            if changed:
                self.start_price.save()
        self.contract.save_price()

    def delete(self, *args, **kwargs):
        """
        Extend родительский метод
        При удалении вызывает метод связанного Contract
        """
        year = self.limit.industry_code.limit_article.source.limit.year
        delete_reestr_cache(year)
        super().delete(*args, **kwargs)
        self.contract.save_price()

    def get_economy(self):
        """Считает экономию"""
        if self.start_price:
            return self.start_price.money - self.money
        return 0

    def get_absolute_url(self):
        """Возвращает ссылку на связанный Contract"""
        return reverse('tenders:contract_detail', args=[self.contract.id])

    def get_money_with_change(self):
        """
        Считает сумму с учетом связанных изменений цены (доп. соглашений)
        """
        delta = (self.contractpricechange_set.all().aggregate(
            m=Sum('delta')
        )['m'] or 0)
        money_with_change = self.money + delta
        return money_with_change

    @classmethod
    def moneys_for_excel_export(cls, year):
        """Возвращает список денег для формирования отчета"""
        return cls.objects.filter(
            limit__industry_code__limit_article__source__limit__year=year
        ).prefetch_related(
            'contract__ticket__tender_type',
            'limit__industry_code__limit_article__source',
        ).select_related(
            'subdivision',
            'start_price',
        )


class ContractPriceChange(models.Model):
    """
    Модель изменения цены контракта, ссылается на экземпляр цены контракта и
    содержит сумму изменения цены
    """
    change = models.ForeignKey(
        'contracts.ContractChange',
        verbose_name='Доп. соглашение',
        on_delete=models.CASCADE)

    price = models.ForeignKey(
        ContractPrice,
        verbose_name='Цена контракта',
        on_delete=models.CASCADE)

    delta = models.DecimalField(
        'Сумма изменения цены',
        max_digits=11,
        decimal_places=2)

    def __str__(self):
        return str(self.delta)

    def save(self, *args, **kwargs):
        """
        Extend родительский метод
        При сохранении вызывает метод связанного Contract
        """
        super().save(*args, **kwargs)
        year = self.price.limit.industry_code.limit_article.source.limit.year
        delete_reestr_cache(year)
        self.change.contract.save_price()

    def delete(self, *args, **kwargs):
        """
        Extend родительский метод
        При удалении вызывает метод связанного Contract
        """
        year = self.price.limit.industry_code.limit_article.source.limit.year
        delete_reestr_cache(year)
        super().delete(*args, **kwargs)
        self.change.contract.save_price()

    def get_absolute_url(self):
        """Возвращает ссылку на связанный Contract"""
        return reverse(
            'contracts:contract_detail',
            args=[self.change.contract.id],
        )
