from rest_framework import serializers

from contracts.models import Contract


class ContractSerializer(serializers.ModelSerializer):
    money = serializers.DecimalField(max_digits=11, decimal_places=2)
    delta = serializers.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        model = Contract
        fields = ('tender', 'num', 'date', 'specif', 'ticket', 'bg_choices',
                  'bank_guar', 'pledge', 'kontragent', 'money', 'delta')
