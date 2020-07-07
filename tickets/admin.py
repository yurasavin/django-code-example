from django.contrib import admin

from .models import Ticket, Filial


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'date', 'worker', 'initiator', 'filial', 'tender_type',
        'under_type', 'status'
    )


admin.site.register(Filial)
