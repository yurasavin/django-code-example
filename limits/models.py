from decimal import Decimal

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Case, Count, F, Sum, Value, When
from django.db.models.functions import Coalesce

from contracts.models import Contract

from tenders.models import Tender

DEF_DECIMAL_DIGITS = 11
DEF_DECIMAL_PLACES = 2
DEF_CHAR_L = 256


class Limit(models.Model):

    year = models.PositiveSmallIntegerField(db_index=True)

    class Meta:
        ordering = ['-year']

    def __str__(self):  # noqa: D105
        return str(self.year)

    @property
    def source_num_field(self):
        """Return deep related source field"""
        return F('industry_code__limit_article__source__num')

    def set_money_to_zero(self):
        """
        Set all related LimitMoney money to 0
        """
        LimitMoney.objects\
            .filter(industry_code__limit_article__source__limit_id=self.id)\
            .update(money=0)


class LimitDateInfo(models.Model):

    date = models.DateField(auto_now_add=True)
    data = JSONField()
    limit = models.ForeignKey(Limit, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['limit', 'date'],
                name='limit_and_date',
            ),
        ]

    def __str__(self):  # noqa: D105
        return f'{self.id}: {self.date}'


class Source(models.Model):

    num = models.PositiveSmallIntegerField(db_index=True)
    name = models.CharField(max_length=DEF_CHAR_L)
    limit = models.ForeignKey(Limit, on_delete=models.CASCADE)

    class Meta:
        ordering = ['num']

    def __str__(self):  # noqa: D105
        return f'{self.name} ({self.num})'

    def get_money(self):
        """
        Return total money
        """
        return LimitMoney.objects\
            .filter(industry_code__limit_article__source_id=self.id)\
            .aggregate(m=Sum('money'))['m']


class LimitArticle(models.Model):

    name = models.CharField(max_length=DEF_CHAR_L)
    num = models.PositiveSmallIntegerField(db_index=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    class Meta:
        ordering = ['num']

    def __str__(self):  # noqa: D105
        return f'{self.num} - {self.name}'


class IndustryCode(models.Model):

    INDUSTRY_CODE_LENGTH = 30

    name = models.CharField(max_length=DEF_CHAR_L)
    num = models.CharField(max_length=INDUSTRY_CODE_LENGTH, db_index=True)
    limit_article = models.ForeignKey(LimitArticle, on_delete=models.CASCADE)

    class Meta:
        ordering = ['num']

    def __str__(self):  # noqa: D105
        return f'{self.num}: {self.name}'


class LimitMoney(models.Model):

    SUBSIDY_CODE_LENGTH = 5

    name = models.CharField(max_length=DEF_CHAR_L)
    sybsidy_code = models.CharField(max_length=SUBSIDY_CODE_LENGTH)
    money = models.DecimalField(max_digits=DEF_DECIMAL_DIGITS,
                                decimal_places=DEF_DECIMAL_PLACES, default=0)
    industry_code = models.ForeignKey(IndustryCode, on_delete=models.CASCADE)

    class Meta:
        ordering = ['sybsidy_code']

    def __str__(self):  # noqa: D105
        return f'{self.name}; {self. money}'


class Debt(models.Model):

    article = models.OneToOneField(LimitArticle, on_delete=models.CASCADE,
                                   null=True)
    money = models.DecimalField(max_digits=DEF_DECIMAL_DIGITS,
                                decimal_places=DEF_DECIMAL_PLACES, default=0)

    def __str__(self):  # noqa: D105
        return f'{self.id}: {self.money}'
