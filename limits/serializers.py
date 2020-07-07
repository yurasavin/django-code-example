from rest_framework import serializers

from limits.models import Limit


class LimitInfoSerializer(serializers.ModelSerializer):
    data = serializers.JSONField()

    class Meta:
        model = Limit
        fields = ('model', 'registration_number', )
