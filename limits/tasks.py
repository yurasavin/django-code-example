from celery import shared_task
from celery.utils.log import get_task_logger

from decimal import Decimal

from django.db import models
from django.db.models import Count, F, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from limits.models import Limit, LimitDateInfo

logger = get_task_logger(__name__)


@shared_task(name='run_limit_info_update')
def run_limits_info_update():
    curr_year = timezone.now().year
    for limit in Limit.objects.filter(year__gte=curr_year):
        logger.info(f'Run update info for limit of {limit.year} year')
        update_limit_info.delay(limit.id)


@shared_task(name='update_limit_info')
def update_limit_info(limit_id):
    limit = Limit.objects.get(id=limit_id)

    limit_data = {}

    sources_total, sources_in_use, sources_used = _get_limit_sources(limit)

    for source_total in sources_total:
        num = source_total['num']
        limit_data[num] = source_total
        source_total['articles'] = {}
        source_total['in_use'] = 0
        source_total['used'] = 0

    for source_in_use in sources_in_use:
        num = source_in_use['num']
        limit_data[num]['in_use'] = source_in_use['in_use']

    for source_used in sources_used:
        num = source_used['num']
        limit_data[num]['used'] = source_used['used_with_delta']

    articles_total, articles_in_use, articles_used = _get_limit_articles(limit)
    for article_total in articles_total:
        source_num = article_total['source_num']
        num = article_total['num']
        limit_data[source_num]['articles'][num] = article_total
        article_total['industry_codes'] = {}
        article_total['in_use'] = 0
        article_total['used'] = 0

    for article_in_use in articles_in_use:
        source_num = article_in_use['source_num']
        num = article_in_use['num']
        limit_data[source_num]['articles'][num]\
            ['in_use'] = article_in_use['in_use']

    for article_used in articles_used:
        source_num = article_used['source_num']
        num = article_used['num']
        limit_data[source_num]['articles'][num]\
            ['used'] = article_used['used_with_delta']

    moneys_total, moneys_in_use, moneys_used = _get_limit_moneys(limit)
    for money_total in moneys_total:
        source_num = money_total['source_num']
        article_num = money_total['article_num']
        money_id = money_total['id']
        limit_data[source_num]['articles'][article_num]['industry_codes']\
            [money_id] = money_total
        money_total['in_use'] = 0
        money_total['used'] = 0

    for money_in_use in moneys_in_use:
        source_num = money_in_use['source_num']
        article_num = money_in_use['article_num']
        money_id = money_in_use['id']
        limit_data[source_num]['articles'][article_num]['industry_codes']\
            [money_id]['in_use'] = money_in_use['in_use']

    for money_used in moneys_used:
        source_num = money_used['source_num']
        article_num = money_used['article_num']
        money_id = money_used['id']
        limit_data[source_num]['articles'][article_num]['industry_codes']\
            [money_id]['used'] = money_used['used_with_delta']

    LimitDateInfo.objects.create(limit=limit, data=limit_data)


def _get_limit_sources(limit):
    """Return money, grouped by sources"""
    qs = limit.limit_moneys\
        .values('industry_code__limit_article__source__num')\
        .order_by('industry_code__limit_article__source__num')

    total = qs.annotate(total=Sum('money'))\
        .values('total', num=limit.source_num_field,
                id=F('industry_code__limit_article__source__id'),
                name=F('industry_code__limit_article__source__name'))

    in_use = _get_in_use(qs).values(
        'in_use', num=limit.source_num_field)

    used = _get_used(qs).values(
        'used_with_delta', num=limit.source_num_field)

    return total, in_use, used


def _get_limit_articles(limit):
    """Return money, grouped by articles"""
    qs = limit.limit_moneys\
        .values(
            'industry_code__limit_article__source__num',
            'industry_code__limit_article__num')\
        .order_by(
            'industry_code__limit_article__source__num',
            'industry_code__limit_article__num')

    total = qs.annotate(
        total=Sum('money'),
        row_span=Count('pk') + Value(1, models.IntegerField()),
        source_num=limit.source_num_field,
        num=F('industry_code__limit_article__num'),
        name=F('industry_code__limit_article__name'),
    ).values('total', 'row_span', 'source_num', 'num', 'name',
             id=F('industry_code__limit_article__id'))

    in_use = _get_in_use(qs).values(
        'in_use',
        source_num=limit.source_num_field,
        num=F('industry_code__limit_article__num'),
    )

    used = _get_used(qs).values(
        'used_with_delta',
        source_num=limit.source_num_field,
        num=F('industry_code__limit_article__num'),
    )

    return total, in_use, used


def _get_limit_moneys(limit):
    """Return limit money"""
    qs = limit.limit_moneys.order_by(
        'industry_code__num', 'industry_code__limit_article__num',
        'industry_code__limit_article__source__num')

    total = qs.annotate(
        source_num=limit.source_num_field,
        article_num=F('industry_code__limit_article__num'),
    ).values(
        'id', 'money', 'industry_code__name', 'industry_code__num',
        'sybsidy_code', 'source_num', 'article_num')

    in_use = _get_in_use(qs).values(
        'id', 'in_use', source_num=limit.source_num_field,
        article_num=F('industry_code__limit_article__num'))

    used = _get_used(qs).values(
        'id', 'used_with_delta', source_num=limit.source_num_field,
        article_num=F('industry_code__limit_article__num'))

    return total, in_use, used


def _get_in_use(queryset):
    """
    Annotate money in work amount to queryset
    """
    return queryset\
        .filter(startprice__tender__status='in_work')\
        .annotate(
            in_use=Coalesce(Sum('startprice__money'), Value(Decimal('0'))))


def _get_used(queryset):
    """
    Annotate used money amount to queryset
    """
    return queryset.annotate(
        used=Sum('contractprice__money', distinct=True),
        delta=Coalesce(
            Sum('contractprice__contractpricechange__delta', distinct=True),
            Value(0, output_field=models.DecimalField()),
        ),
    ).annotate(used_with_delta=F('used') + F('delta'))
