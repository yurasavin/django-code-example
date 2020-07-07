from django import forms

from make_docs.my_widgets import DateWithCalendarWidget

from .models import Contract, ContractChange


class ContractForm(forms.ModelForm):
    """Форма для контракта, добавляет класс для виджета выбора даты"""
    date = forms.DateField(label='Дата', widget=DateWithCalendarWidget)

    class Meta:
        model = Contract
        exclude = [
            'ticket', 'tender', 'price', 'other_ikz_part', 'part_of_ikz',
        ]


class ContractFormWithIkz(forms.ModelForm):
    """Форма для контракта, с ИКЗ"""
    date = forms.DateField(label='Дата', widget=DateWithCalendarWidget)

    class Meta:
        model = Contract
        exclude = [
            'ticket', 'tender', 'price', 'other_ikz_part',
        ]


class ContractChangeForm(forms.ModelForm):
    """Форма для допика, добавляет класс для виджета выбора даты"""

    date = forms.DateField(label='Дата', widget=DateWithCalendarWidget)

    class Meta:
        model = ContractChange
        fields = ['num', 'date', 'reason']
