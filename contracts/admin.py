from django.contrib import admin

from prices.admin import ContractPriceChangeInline, ContractPriceInline

from .models import Contract, ContractChange, ContractNum, PartOfIkz

admin.site.register(ContractNum)
admin.site.register(PartOfIkz)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    inlines = [ContractPriceInline]
    list_display = (
        'num', 'date', 'price', 'kontragent', 'bank_guar', 'pledge',
    )


@admin.register(ContractChange)
class ContractChangeAdmin(admin.ModelAdmin):
    inlines = [ContractPriceChangeInline]
    list_display = ('num', 'date', 'contract', 'reason')
