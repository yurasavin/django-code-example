from decimal import Decimal

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

    def get_in_use(self, queryset):
        """
        Return amount of money in work
        """
        return queryset\
            .filter(startprice__tender__status='in_work')\
            .annotate(in_use=Coalesce(
                Sum('startprice__money'), Value(Decimal('0'))))

    def get_used(self, queryset):
        """
        Return amount of used money
        """
        return queryset.annotate(
            used=Sum('contractprice__money', distinct=True),
            delta=Coalesce(
                Sum(
                    'contractprice__contractpricechange__delta',
                    distinct=True,
                ),
                Value(0, output_field=models.DecimalField()),
            ),
        ).annotate(
            used_with_delta=F('used') + F('delta'),
        )

    def get_subdivisions_sources(self):
        """
        Return money, grouped by sources and subdivisions
        """
        qs = Subdivision.objects\
            .filter(source__limit_id=self.id)\
            .values('source__num', 'num')\
            .order_by('source__num', 'num')

        total_and_used = self.get_used(qs).values(
            'id', 'source__num', 'num', 'money', used=F('used_with_delta'))

        in_use = self.get_in_use(qs).values(
            'source__num', 'num', 'in_use')

        return total_and_used, in_use

    def get_sources_data(self):
        """Return money, grouped by sources"""
        qs = LimitMoney.objects\
            .filter(industry_code__limit_article__source__limit_id=self.id)\
            .values('industry_code__limit_article__source__num')\
            .order_by('industry_code__limit_article__source__num')

        total = qs.annotate(total=Sum('money'))\
            .values('total', num=self.source_num_field,
                    id=F('industry_code__limit_article__source__id'),
                    name=F('industry_code__limit_article__source__name'))

        in_use = self.get_in_use(qs).values(
            'in_use', num=self.source_num_field)

        used = self.get_used(qs).values(
            'used_with_delta', num=self.source_num_field)

        return total, in_use, used

    def get_articles_data(self):
        """Return money, grouped by articles"""
        qs = LimitMoney.objects\
            .filter(industry_code__limit_article__source__limit_id=self.id)\
            .values(
                'industry_code__limit_article__source__num',
                'industry_code__limit_article__num',
            )\
            .order_by(
                'industry_code__limit_article__source__num',
                'industry_code__limit_article__num',
            )

        total = qs.annotate(
            total=Sum('money'),
            row_span=Count('pk') + Value(1, models.IntegerField()),
            source_num=self.source_num_field,
            num=F('industry_code__limit_article__num'),
            name=F('industry_code__limit_article__name'),
        ).values('total', 'row_span', 'source_num', 'num', 'name',
                 id=F('industry_code__limit_article__id'))

        in_use = self.get_in_use(qs).values(
            'in_use',
            source_num=self.source_num_field,
            num=F('industry_code__limit_article__num'),
        )

        used = self.get_used(qs).values(
            'used_with_delta',
            source_num=self.source_num_field,
            num=F('industry_code__limit_article__num'),
        )

        return total, in_use, used

    def get_moneys_data(self):
        """Return limit money"""
        qs = LimitMoney.objects.filter(
            industry_code__limit_article__source__limit_id=self.id,
        ).order_by(
            'industry_code__limit_article__source__num',
            'industry_code__limit_article__num',
            'industry_code__num',
        )

        total = qs.annotate(
            source_num=self.source_num_field,
            article_num=F('industry_code__limit_article__num'),
        ).values(
            'id', 'money', 'industry_code__name', 'industry_code__num',
            'sybsidy_code', 'source_num', 'article_num')

        in_use = self.get_in_use(qs).values(
            'id', 'in_use', source_num=self.source_num_field,
            article_num=F('industry_code__limit_article__num'))

        used = self.get_used(qs).values(
            'id', 'used_with_delta', source_num=self.source_num_field,
            article_num=F('industry_code__limit_article__num'))

        return total, in_use, used

    def get_limit_data(self):  # noqa: WPS210
        """
        Return info about limit
        """
        limit_data = {}

        sources_total, sources_in_use, sources_used = self.get_sources_data()
        for source_total in sources_total:
            num = source_total['num']
            limit_data[num] = source_total
            source_total['articles'] = {}
            source_total['subdivisions'] = {}
            source_total['in_use'] = 0
            source_total['used'] = 0

        for source_in_use in sources_in_use:
            num = source_in_use['num']
            limit_data[num]['in_use'] = source_in_use['in_use']

        for source_used in sources_used:
            num = source_used['num']
            limit_data[num]['used'] = source_used['used_with_delta']

        subdivisions_total_and_used, subdivisions_in_use = self.get_subdivisions_sources()  # noqa: E501
        for subdivision_total in subdivisions_total_and_used:
            source_num = subdivision_total['source__num']
            num = subdivision_total['num']
            limit_data[source_num]['subdivisions'][num] = subdivision_total  # noqa: E501, WPS204
            subdivision_total['in_use'] = 0

        for subdivision in subdivisions_in_use:
            source_num = subdivision['source__num']
            num = subdivision['num']
            limit_data[source_num]['subdivisions'][num]['in_use'] = subdivision['in_use']  # noqa: E501

        articles_total, articles_in_use, articles_used = self.get_articles_data()  # noqa: E501
        for article_total in articles_total:
            source_num = article_total['source_num']
            num = article_total['num']
            limit_data[source_num]['articles'][num] = article_total  # noqa: E501, WPS204
            article_total['industry_codes'] = {}
            article_total['in_use'] = 0
            article_total['used'] = 0

        for article_in_use in articles_in_use:
            source_num = article_in_use['source_num']
            num = article_in_use['num']
            limit_data[source_num]['articles'][num]['in_use'] = article_in_use['in_use']  # noqa: E501

        for article_used in articles_used:
            source_num = article_used['source_num']
            num = article_used['num']
            limit_data[source_num]['articles'][num]['used'] = article_used['used_with_delta']  # noqa: E501

        moneys_total, moneys_in_use, moneys_used = self.get_moneys_data()
        for money_total in moneys_total:
            source_num = money_total['source_num']
            article_num = money_total['article_num']
            money_id = money_total['id']
            limit_data[source_num]['articles'][article_num]['industry_codes'][money_id] = money_total  # noqa: E501, WPS219
            money_total['in_use'] = 0
            money_total['used'] = 0

        for money_in_use in moneys_in_use:
            source_num = money_in_use['source_num']
            article_num = money_in_use['article_num']
            money_id = money_in_use['id']
            limit_data[source_num]['articles'][article_num]['industry_codes'][money_id]['in_use'] = money_in_use['in_use']  # noqa: E501, WPS221, WPS219

        for money_used in moneys_used:
            source_num = money_used['source_num']
            article_num = money_used['article_num']
            money_id = money_used['id']
            limit_data[source_num]['articles'][article_num]['industry_codes'][money_id]['used'] = money_used['used_with_delta']  # noqa: E501, WPS221, WPS219

        return limit_data

    def set_money_to_zero(self):
        """
        Set all related LimitMoney money to 0
        """
        LimitMoney.objects\
            .filter(industry_code__limit_article__source__limit_id=self.id)\
            .update(money=0)


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

    def get_contracts(self):
        """
        Return contracts with amount
        """
        return Contract.objects.filter(
            contractprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
        ).annotate(
            money=Case(
                When(
                    contractprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
                    then=Sum('contractprice__money', distinct=True),
                ),
                output_field=models.DecimalField(),
            ),
            delta=Case(
                When(
                    contractprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
                    then=Sum(
                        'contractprice__contractpricechange__delta',
                        distinct=True,
                    ),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type',
            'ticket__filial',
            'ticket__worker',
        )

    def get_tenders_in_work(self):
        """
        Return tenders in process with amount
        """
        return Tender.objects.filter(
            status='in_work',
            startprice__limit__industry_code__limit_article__source_id=self.id,
        ).annotate(
            money=Case(
                When(
                    startprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
                    then=Sum('startprice__money'),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type', 'ticket__filial', 'ticket__worker')


class LimitArticle(models.Model):

    name = models.CharField(max_length=DEF_CHAR_L)
    num = models.PositiveSmallIntegerField(db_index=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    class Meta:
        ordering = ['num']

    def __str__(self):  # noqa: D105
        return f'{self.num} - {self.name}'

    def get_contracts(self):
        """
        Return contracts with amount
        """
        return Contract.objects.filter(
            contractprice__limit__industry_code__limit_article_id=self.id,
        ).annotate(
            money=Case(
                When(
                    contractprice__limit__industry_code__limit_article_id=self.id,  # noqa: E501
                    then=Sum('contractprice__money', distinct=True),
                ),
                output_field=models.DecimalField(),
            ),
            delta=Case(
                When(
                    contractprice__limit__industry_code__limit_article_id=self.id,  # noqa: E501
                    then=Sum(
                        'contractprice__contractpricechange__delta',
                        distinct=True,
                    ),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type', 'ticket__filial', 'ticket__worker')

    def get_tenders_in_work(self):
        """
        Return tenders in process with amount
        """
        return Tender.objects.filter(
            status='in_work',
            startprice__limit__industry_code__limit_article_id=self.id,
        ).annotate(
            money=Case(
                When(
                    startprice__limit__industry_code__limit_article_id=self.id,
                    then=Sum('startprice__money'),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type', 'ticket__filial', 'ticket__worker')


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

    def get_contracts(self):
        """
        Return contracts with amount
        """
        return Contract.objects.filter(
            contractprice__limit_id=self.id,
        ).annotate(
            money=Case(
                When(
                    contractprice__limit_id=self.id,
                    then=Sum('contractprice__money', distinct=True),
                ),
                output_field=models.DecimalField(),
            ),
            delta=Case(
                When(
                    contractprice__limit_id=self.id,
                    then=Sum(
                        'contractprice__contractpricechange__delta',
                        distinct=True,
                    ),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type', 'ticket__filial', 'ticket__worker')

    def get_tenders_in_work(self):
        """
        Return tenders with amount
        """
        return Tender.objects.filter(
            status='in_work',
            startprice__limit_id=self.id,
        ).annotate(
            money=Case(
                When(
                    startprice__limit_id=self.id,
                    then=Sum('startprice__money'),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type', 'ticket__filial', 'ticket__worker')


class Subdivision(models.Model):

    SUBDIVISION_NUM_LENGTH = 4

    name = models.CharField(max_length=DEF_CHAR_L)
    num = models.CharField(max_length=SUBDIVISION_NUM_LENGTH, db_index=True)
    money = models.DecimalField(max_digits=DEF_DECIMAL_DIGITS,
                                decimal_places=DEF_DECIMAL_PLACES, default=0)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)

    class Meta:
        ordering = ['num']

    def __str__(self):  # noqa: D105
        return self.num

    def get_contracts(self):
        """
        Return contracts with amount
        """
        return Contract.objects.filter(
            contractprice__subdivision_id=self.id,
        ).annotate(
            money=Case(
                When(
                    contractprice__subdivision_id=self.id,
                    then=Sum('contractprice__money', distinct=True),
                ),
                output_field=models.DecimalField(),
            ),
            delta=Case(
                When(
                    contractprice__subdivision_id=self.id,
                    then=Sum(
                        'contractprice__contractpricechange__delta',
                        distinct=True,
                    ),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type', 'ticket__filial', 'ticket__worker')

    def get_tenders_in_work(self):
        """
        Return tenders with amount
        """
        return Tender.objects.filter(
            status='in_work',
            startprice__subdivision_id=self.id,
        ).annotate(
            money=Case(
                When(
                    startprice__subdivision_id=self.id,
                    then=Sum('startprice__money'),
                ),
                output_field=models.DecimalField(),
            ),
        ).prefetch_related(
            'ticket__tender_type', 'ticket__filial', 'ticket__worker')


class Debt(models.Model):

    article = models.OneToOneField(LimitArticle, on_delete=models.CASCADE,
                                   null=True)
    money = models.DecimalField(max_digits=DEF_DECIMAL_DIGITS,
                                decimal_places=DEF_DECIMAL_PLACES, default=0)

    def __str__(self):  # noqa: D105
        return f'{self.id}: {self.money}'
