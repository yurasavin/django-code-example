from django import forms

from tenders.models import Tender
from contracts.models import Contract

from .models import StartPrice


class PriceForm(forms.ModelForm):
    """Базовая форма для создания НМЦК, либо цены контракта"""

    year = forms.ChoiceField(label='Год финансирования')
    source = forms.ChoiceField(label='Источник')
    article = forms.ChoiceField(label='Статья')
    industry_code = forms.ChoiceField(label='Отраслевой код')
    limit_money = forms.ChoiceField(label='Код субсидии')
    subdivision = forms.ChoiceField(label='Подраздел')

    field_order = [
        'year',
        'source',
        'article',
        'industry_code',
        'limit_money',
        'subdivision',
        'money'
    ]

    class Meta:
        model = StartPrice
        fields = ['money', ]

    def __init__(self, *args, **kwargs):
        """
        На основании заявки формирует начальные данные для полей формы
        """

        if 'tender' in kwargs['initial'].keys():
            tender_id = kwargs['initial'].pop('tender')
            tender = Tender.objects.filter(id=tender_id).prefetch_related(
                'ticket__year'
            )[0]
            years_query = tender.ticket.year.all().prefetch_related(
                'source_set__limitarticle_set__industrycode_set__limitmoney_set')
        else:
            contract_id = kwargs['initial'].pop('contract')
            contract = Contract.objects.filter(
                id=contract_id
            ).prefetch_related(
                'ticket__year'
            )[0]
            years_query = contract.ticket.year.all().prefetch_related(
                'source_set__limitarticle_set__industrycode_set__limitmoney_set')

        super(PriceForm, self).__init__(*args, **kwargs)

        default_choices = [('default', '-------'), ]
        self.fields['year'].choices = default_choices.copy() + (
            [(year.year, year.year) for year in years_query]
        )

        # Проходим по каждому году и формируем группы чоисов
        source_items = default_choices.copy()
        subdivision_items = default_choices.copy()
        article_items = default_choices.copy()
        industry_code_items = default_choices.copy()
        money_items = default_choices.copy()
        for year in years_query:
            sources = []
            for source in year.source_set.all():
                sources.append(
                    (source.id, source)
                )
                subdivisions = []
                for subdivision in source.subdivision_set.all():
                    subdivisions.append(
                        (subdivision.id, subdivision.num)
                    )
                articles = []
                for article in source.limitarticle_set.all():
                    articles.append(
                        (article.id, article)
                    )
                    industry_codes = []
                    for industry_code in article.industrycode_set.all():
                        industry_codes.append(
                            (industry_code.id, industry_code)
                        )
                        moneys = []
                        for money in industry_code.limitmoney_set.all():
                            moneys.append(
                                (money.id, money.sybsidy_code)
                            )
                        money_items.append(
                            (industry_code.id, moneys)
                        )
                    industry_code_items.append(
                        (article.id, industry_codes)
                    )
                subdivision_items.append(
                    (source.id, subdivisions)
                )
                article_items.append(
                    (source.id, articles)
                )
            source_items.append(
                (year.year, sources)
            )
        self.fields['source'].choices = source_items
        self.fields['article'].choices = article_items
        self.fields['industry_code'].choices = industry_code_items
        self.fields['limit_money'].choices = money_items
        self.fields['subdivision'].choices = subdivision_items

    def clean_limit_money(self):
        """проверяет что выбраны лимиты"""
        limit_money = self.cleaned_data['limit_money']
        if limit_money == 'default':
            raise forms.ValidationError(
                "Необходимо выбрать источник финансирования"
            )
        return limit_money

    def clean_subdivision(self):
        """проверяет что выбраны подраздел"""
        subdivision = self.cleaned_data['subdivision']
        if subdivision == 'default':
            raise forms.ValidationError(
                "Необходимо выбрать подраздел"
            )
        return subdivision
