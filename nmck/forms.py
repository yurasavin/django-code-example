from decimal import Decimal, ROUND_HALF_UP
from math import sqrt

from django import forms


class NmckPositionForm(forms.Form):
    """
    Форма НЦМК
    """
    name = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={'form': 'positions_form'})
    )
    type_of_size = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={'form': 'positions_form'})
    )
    num = forms.DecimalField(
        required=True,
        widget=forms.widgets.NumberInput(attrs={'form': 'positions_form'}),
        max_digits=10,
        decimal_places=1
    )
    price1 = forms.DecimalField(
        required=True,
        widget=forms.widgets.NumberInput(attrs={'form': 'positions_form'}),
        max_digits=10,
        decimal_places=2
        )
    price2 = forms.DecimalField(
        required=True,
        widget=forms.widgets.NumberInput(attrs={'form': 'positions_form'}),
        max_digits=10,
        decimal_places=2
        )
    price3 = forms.DecimalField(
        required=True,
        widget=forms.widgets.NumberInput(attrs={'form': 'positions_form'}),
        max_digits=10,
        decimal_places=2
        )

    def clean(self):
        """
        Проверяет коэффициент вариации и добавляет его в cleaned_data, а так же
        среднее значение, сумму и стандартное отклонение
        """
        cleaned_data = super().clean()
        price1 = cleaned_data.get('price1')
        price2 = cleaned_data.get('price2')
        price3 = cleaned_data.get('price3')
        num = cleaned_data.get('num')
        name = cleaned_data.get('name')
        type_of_size = cleaned_data.get('type_of_size')
        if None in [price1, price2, price3, num, name, type_of_size]:
            raise forms.ValidationError('Заполнены не все поля')
        avrg = (price1 + price2 + price3) / 3
        standard_deviation = sqrt(
            (
                pow(price1 - avrg, 2) +
                pow(price2 - avrg, 2) +
                pow(price3 - avrg, 2)
            ) / 2
        )
        variation = (standard_deviation / float(avrg) * 100)
        if variation > 33:
            raise forms.ValidationError('Коэффициент вариации превышает 33%')
        quant = Decimal('1.00')
        cleaned_data['avrg'] = avrg.quantize(quant, ROUND_HALF_UP)
        cleaned_data['standard_deviation'] = Decimal(
            standard_deviation
        ).quantize(quant, ROUND_HALF_UP)
        cleaned_data['variation'] = Decimal(variation).quantize(
            quant, ROUND_HALF_UP
        )
        cleaned_data['summ'] = cleaned_data['avrg'] * num


NmckPositionFormSet = forms.formset_factory(
    NmckPositionForm, extra=9,  min_num=1, validate_min=True
)
