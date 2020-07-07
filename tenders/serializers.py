from rest_framework import serializers

from tenders.models import Tender


class TenderSerializer(serializers.ModelSerializer):
    money = serializers.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        model = Tender
        fields = ('ikz', 'num', 'status', 'smp', 'ticket', 'money')
