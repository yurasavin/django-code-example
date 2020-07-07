from django.contrib import admin

from .models import StartPrice, ContractPrice, ContractPriceChange

admin.site.register(StartPrice)
admin.site.register(ContractPrice)


class StartPriceInline(admin.TabularInline):
    """Инлайн НМЦК для добавления отображения в другой модели"""
    model = StartPrice
    extra = 0


class ContractPriceInline(admin.TabularInline):
    """Инлайн цены контракта для добавления отображения в другой модели"""
    model = ContractPrice
    extra = 0


class ContractPriceChangeInline(admin.TabularInline):
    """Инлайн цены доп соглашения для добавления отображения в другой модели"""
    model = ContractPriceChange
    extra = 0
