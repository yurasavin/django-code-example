from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from prices.models import ContractPrice, ContractPriceChange

from tickets.models import Ticket

from .forms import ContractChangeForm, ContractForm, ContractFormWithIkz
from .models import Contract, ContractChange, ContractNum, PartOfIkz


class ContractCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView,
):
    """Представление для создания контракта"""
    model = Contract
    permission_required = ['contracts.add_contract']
    form_class = ContractForm

    def get_form_class(self):
        ticket_id = self.kwargs['ticket']
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.tender_type.ep_and_use_ikz:
            return ContractFormWithIkz
        return super().get_form_class()

    def form_valid(self, form):
        """Определяет заявку, тендер, и сохраняет контракт"""
        ticket_id = self.kwargs['ticket']
        ticket = Ticket.objects.get(id=ticket_id)
        tender = ticket.tender if hasattr(ticket, 'tender') else None
        self.object = Contract.objects.create(
            ticket=ticket,
            tender=tender,
            **form.cleaned_data,
        )
        # Увеличивает номер если необходимо
        num_storage = ContractNum.objects.get(pk=1)
        num_storage.increase_num(ticket, form.cleaned_data['num'])

        # Увеличивает ИКЗ если надо, добавляем икз к контракту
        if ticket.tender_type.ep_and_use_ikz:
            year = ticket.date.year
            part_of_ikz = PartOfIkz.objects.get(year=year)
            part_of_ikz.num_27_29 += 1
            part_of_ikz.save()

            self.object.other_ikz_part = part_of_ikz
            self.object.save()

        # Создаем цены если необходимо
        buy_from_singe_supplier = ticket.tender_type.buy_from_singe_supplier
        need_publicate = ticket.tender_type.need_publicate
        if buy_from_singe_supplier and need_publicate:
            for price in tender.startprice_set.all():
                ContractPrice.objects.create(
                    limit=price.limit,
                    money=price.money,
                    start_price=price,
                    contract=self.object,
                    subdivision=price.subdivision)
        elif ticket.tender_type.need_publicate:
            for price in tender.startprice_set.all():
                ContractPrice.objects.create(
                    limit=price.limit,
                    money=0,
                    start_price=price,
                    contract=self.object,
                    subdivision=price.subdivision)
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        """Добавляет номер контракта для закупок до 100 т.р. по 223-ФЗ"""
        initial = super().get_initial()
        ticket_id = self.kwargs['ticket']
        ticket = Ticket.objects.get(pk=ticket_id)

        # Добавляем в форму номер если предусмотрено споосбом закупки
        if ticket.tender_type.use_default_num:
            initial['num'] = ticket.get_num()

        # Добавляем ИКЗ для до 600 т.р.
        if ticket.tender_type.ep_and_use_ikz:
            year = ticket.date.year
            part_of_ikz = PartOfIkz.objects.get(year=year)
            initial['part_of_ikz'] = part_of_ikz.num_27_29

        # Добавляем в форму данные об обеспечении если известно что они нулевые
        if ticket.tender_type.dont_need_bank_guar():
            initial['bank_guar'] = False
            initial['pledge'] = 0
        return initial


class ContractUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    """Представление для изменения контракта"""
    model = Contract
    permission_required = ['contracts.change_contract']
    form_class = ContractForm

    def get_form_class(self):
        contract_id = self.kwargs['pk']
        ticket = Ticket.objects.get(contract=contract_id)
        if ticket.tender_type.ep_and_use_ikz:
            return ContractFormWithIkz
        return super().get_form_class()


class ContractDetailView(LoginRequiredMixin, generic.DetailView):
    """Представление для просмотра контракта"""
    model = Contract


class ContractForBuhView(LoginRequiredMixin, generic.DetailView):
    """Представление для отображения данных по контракту для бухгалтерии"""
    model = Contract
    template_name = 'contracts/contract_for_buh.html'


class ContarctDeleteView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        DeleteView,
):
    """Представление для удаления контракта"""
    model = Contract
    success_url = reverse_lazy('tickets:reestr')
    permission_required = ['contracts.delete_contract']


class ContractChangeCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView,
):
    """Представление для создания контракта"""
    model = ContractChange
    permission_required = ['contracts.add_contractchange']
    form_class = ContractChangeForm

    def form_valid(self, form):
        """
        Добавляет к экземпляру контракт, сохраняет и создает
        экземпляры изменения цены контракта
        """
        contract_id = self.kwargs['contract']
        contract = Contract.objects.get(id=contract_id)
        self.object = ContractChange.objects.create(
            contract=contract,
            **form.cleaned_data,
        )
        # Создаем изменения цен контракта
        for price in contract.contractprice_set.all():
            ContractPriceChange.objects.create(
                change=self.object,
                price=price,
                delta=0,
            )
        return HttpResponseRedirect(self.get_success_url())


class ContractChangeDeleteView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        DeleteView,
):
    """Представление для удаления доп соглашения"""
    model = ContractChange
    permission_required = ['contracts.delete_contractchange']

    def get_success_url(self):
        return reverse_lazy(
            'contracts:contract_detail',
            args=[self.kwargs['contract']],
        )


class ContractChangeUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView,
):
    """Представление для изменения доп соглашения"""
    model = ContractChange
    permission_required = ['contracts.change_contractchange']
    form_class = ContractChangeForm
