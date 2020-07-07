from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import FormView
from django.http import HttpResponseRedirect

from contracts.models import Contract
from tenders.models import Tender
from limits.models import LimitMoney, Subdivision

from .forms import PriceForm
from .models import StartPrice, ContractPrice, ContractPriceChange


class StartPriceBaseView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        FormView
        ):
    """Базовое представление для создания/изменения НМЦК"""
    permission_required = ['prices.add_startprice']
    form_class = PriceForm
    template_name = 'prices/sp_create.html'

    def get_success_url(self):
        """Возвращает ссылку на страницу тендера"""
        tender = self.kwargs.get('tender')
        if not tender:
            price_id = self.kwargs['price']
            price = StartPrice.objects.get(id=price_id)
            tender = price.tender.id
        return reverse_lazy(
            'tenders:tender_detail', args=[tender]
        )


class StartPriceCreateView(StartPriceBaseView):
    """Представление для создания НМЦК"""

    def get_initial(self):
        """Добавляет тендер в инитиал формы"""
        initial = super().get_initial()
        initial['tender'] = self.kwargs['tender']
        return initial

    def form_valid(self, form):
        """Сохраняет экземпляр цены"""
        tender_id = self.kwargs['tender']
        tender = Tender.objects.get(id=tender_id)
        limit = LimitMoney.objects.get(id=form.cleaned_data['limit_money'])
        subdivision = Subdivision.objects.get(
            id=form.cleaned_data['subdivision']
        )
        tender.startprice_set.create(
            money=form.cleaned_data['money'],
            limit=limit,
            subdivision=subdivision,
        )
        return super().form_valid(form)


class StartPriceUpdateView(StartPriceBaseView):
    """Представление для изменения НМЦК"""

    def get_initial(self):
        """Добавляет данные в инитиал формы"""
        initial = super().get_initial()
        price_id = self.kwargs['price']
        price = StartPrice.objects.filter(id=price_id).prefetch_related(
            'limit__industry_code__limit_article__source__limit'
        )[0]
        initial['year'] = (
            price.limit.industry_code.limit_article.source.limit.year
        )
        initial['source'] = price.limit.industry_code.limit_article.source.id
        initial['article'] = price.limit.industry_code.limit_article.id
        initial['industry_code'] = price.limit.industry_code.id
        initial['limit_money'] = price.limit.id
        initial['subdivision'] = price.subdivision.id
        initial['money'] = price.money
        initial['tender'] = price.tender.id
        return initial

    def form_valid(self, form):
        """Сохраняет экземпляр цены"""
        price_id = self.kwargs['price']
        price = StartPrice.objects.get(id=price_id)
        price.limit = LimitMoney.objects.get(
            id=form.cleaned_data['limit_money']
        )
        price.subdivision = Subdivision.objects.get(
            id=form.cleaned_data['subdivision']
        )
        price.money = form.cleaned_data['money']
        price.save()
        return super().form_valid(form)


class StartPriceCopyView(StartPriceUpdateView):
    """Копирует начальные значения другой цены для быстрого заполнения"""
    def form_valid(self, form):
        """Сохраняет экземпляр цены"""
        tender_id = self.kwargs['tender']
        tender = Tender.objects.get(id=tender_id)
        limit = LimitMoney.objects.get(id=form.cleaned_data['limit_money'])
        subdivision = Subdivision.objects.get(
            id=form.cleaned_data['subdivision']
        )
        tender.startprice_set.create(
            money=form.cleaned_data['money'],
            limit=limit,
            subdivision=subdivision,
        )
        return HttpResponseRedirect(self.get_success_url())


class StartPriceDeleteView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        DeleteView):
    """Представление для удаления НМЦК"""
    model = StartPrice
    permission_required = ['prices.delete_startprice']

    def get_success_url(self):
        """Возвращает ссылку на закупку"""
        return reverse_lazy(
            'tenders:tender_detail', args=[self.kwargs['tender']]
        )


class ContractPriceBaseView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        FormView
        ):
    """Базовое представление для создания/изменения цены контракта"""
    permission_required = ['prices.add_contractprice']
    form_class = PriceForm
    template_name = 'prices/cp_create.html'

    def get_success_url(self):
        """Возвращает ссылку на страницу тендера"""
        contract = self.kwargs.get('contract')
        if not contract:
            price_id = self.kwargs['pk']
            price = ContractPrice.objects.get(id=price_id)
            contract = price.contract.id
        return reverse_lazy(
            'contracts:contract_detail', args=[contract]
        )


class ContractPriceCreateView(ContractPriceBaseView):
    """Представление для создания цены контракта"""

    def get_initial(self):
        """Добавляет контракт в инитиал формы"""
        initial = super().get_initial()
        initial['contract'] = self.kwargs['contract']
        return initial

    def form_valid(self, form):
        """Сохраняет экземпляр цены"""
        contract_id = self.kwargs['contract']
        contract = Contract.objects.get(id=contract_id)
        limit = LimitMoney.objects.get(id=form.cleaned_data['limit_money'])
        subdivision = Subdivision.objects.get(
            id=form.cleaned_data['subdivision']
        )
        contract.contractprice_set.create(
            money=form.cleaned_data['money'],
            limit=limit,
            subdivision=subdivision,
        )
        return super().form_valid(form)


class ContractPriceUpdateView(ContractPriceBaseView):
    """Представление для изменения цены контракта"""

    def get_initial(self):
        """Добавляет данные в инитиал формы"""
        initial = super().get_initial()
        price_id = self.kwargs['pk']
        price = ContractPrice.objects.filter(id=price_id).prefetch_related(
            'limit__industry_code__limit_article__source__limit'
        )[0]
        initial['year'] = (
            price.limit.industry_code.limit_article.source.limit.year
        )
        initial['source'] = price.limit.industry_code.limit_article.source.id
        initial['article'] = price.limit.industry_code.limit_article.id
        initial['industry_code'] = price.limit.industry_code.id
        initial['limit_money'] = price.limit.id
        initial['subdivision'] = price.subdivision.id
        initial['money'] = price.money
        initial['contract'] = price.contract.id
        return initial

    def form_valid(self, form):
        """Сохраняет экземпляр цены"""
        price_id = self.kwargs['pk']
        price = ContractPrice.objects.get(id=price_id)
        price.limit = LimitMoney.objects.get(
            id=form.cleaned_data['limit_money']
        )
        price.subdivision = Subdivision.objects.get(
            id=form.cleaned_data['subdivision']
        )
        price.money = form.cleaned_data['money']
        price.save()
        return super().form_valid(form)


class ContractPriceCopyView(ContractPriceUpdateView):
    """Копирует начальные значения другой цены для быстрого заполнения"""

    def form_valid(self, form):
        """Сохраняет экземпляр цены"""
        contract_id = self.kwargs['contract']
        contract = Contract.objects.get(id=contract_id)
        limit = LimitMoney.objects.get(id=form.cleaned_data['limit_money'])
        subdivision = Subdivision.objects.get(
            id=form.cleaned_data['subdivision']
        )
        contract.contractprice_set.create(
            money=form.cleaned_data['money'],
            limit=limit,
            subdivision=subdivision,
        )
        return HttpResponseRedirect(self.get_success_url())


class ContractPriceDeleteView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        DeleteView):
    """Представление для удаления цены контракта"""
    model = ContractPrice
    permission_required = ['prices.delete_contractprice']

    def get_success_url(self):
        """Возвращает ссылку на контракт"""
        return reverse_lazy(
            'contracts:contract_detail', args=[self.kwargs['contract']]
        )


class ContractPriceChangeDeleteView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        DeleteView):
    model = ContractPriceChange
    permission_required = ['prices.delete_contractpricechange']

    def get_success_url(self):
        """Возвращает ссылку на контракт"""
        return reverse_lazy(
            'contracts:contract_detail', args=[self.kwargs['contract']]
        )


class ContractPriceChangeUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    model = ContractPriceChange
    fields = ['delta']
    permission_required = ['prices.change_contractpricechange']
