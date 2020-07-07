from datetime import date

from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from limits.models import Limit

from .models import Ticket


class TicketHomeView(LoginRequiredMixin, generic.ListView):
    """Отображает статистику на главной странице"""
    model = Ticket
    template_name_suffix = '_home'

    def get_queryset(self):
        return self.model.objects.filter(status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = context['ticket_list']
        fz_223 = queryset.filter(tender_type__law=223)
        context['fz_223_all'] = fz_223.count()
        context['fz_223_ep'] = fz_223.filter(
            tender_type__buy_from_singe_supplier=True
        ).count()
        context['fz_223_concurent'] = (
            context['fz_223_all'] - context['fz_223_ep']
        )
        fz_44 = queryset.filter(tender_type__law=44)
        context['fz_44_all'] = fz_44.count()
        context['fz_44_ep'] = fz_44.filter(
            tender_type__buy_from_singe_supplier=True
        ).count()
        context['fz_44_concurent'] = (
            context['fz_44_all'] - context['fz_44_ep']
        )
        return context


class TicketCreate(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView):
    """Представление для создания тикета"""
    permission_required = ['tenders.add_ticket']
    model = Ticket
    fields = '__all__'

    def form_valid(self, form):
        """
        Расширяет родительский метод. Дважды сохраняет инстанс,
        чтобы сбросить кэш после создания связи м2м поля year
        """
        response = super().form_valid(form)
        self.object.save()
        return response


class TicketUpdate(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView):
    """Представление для изменения тикета"""
    permission_required = ['tickets.change_ticket']
    model = Ticket
    fields = '__all__'

    def form_valid(self, form):
        """
        Расширяет родительский метод. Дважды сохраняет инстанс,
        чтобы сбросить кэш после создания связи м2м поля year
        """
        response = super().form_valid(form)
        self.object.save()
        return response


class TicketDelete(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        DeleteView):
    """Представление для удаления тикета"""
    permission_required = ['tickets.delete_ticket']
    model = Ticket
    success_url = reverse_lazy('tickets:reestr')


class TicketsListView(LoginRequiredMixin, generic.ListView):
    """
    Показывает тикеты за выбранный год,
    если url не содержит год, то показывает текущий
    """

    template_name = 'tickets/reestr.html'

    def get_queryset(self):
        """Берет год из урла, если его нет то определяет текущий год"""
        year = self.kwargs.get('year')
        if not year:
            year = date.today().year
        self.year = year
        objects = Ticket.objects.filter(
            year__year=year,
        ).select_related(
            'worker', 'filial', 'tender_type', 'tender', 'contract'
        ).defer(
            'tender__ikz', 'contract__specif'
        )
        return objects

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст
        year - текущий год
        years - список всех лет по лимитам
        """
        context = super().get_context_data(**kwargs)
        context['years'] = [limit.year for limit in Limit.objects.all()]
        context['year'] = self.year
        return context


class WorkerCurrentTicketsListView(LoginRequiredMixin, generic.ListView):
    """
    Показывает заявки в работе у пользователя
    """
    model = Ticket
    template_name = 'tickets/my_current_tickets.html'

    def get_queryset(self):
        """Фильтрует только заявки пользователя"""
        worker = self.kwargs.get('worker')
        worker = worker if worker else self.request.user
        queryset = self.model.objects.filter(
            worker=worker, status=True,
        ).select_related(
            'filial', 'tender_type', 'tender', 'contract'
        ).defer(
            'tender__ikz', 'contract__specif'
        )
        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст
        workers - список пользователей
        """
        context = super().get_context_data(**kwargs)
        workers = Ticket.objects.filter(
            status=True
        ).values_list(
            'worker', 'worker__last_name'
        ).distinct('worker').order_by('worker')
        context['workers'] = workers
        return context
