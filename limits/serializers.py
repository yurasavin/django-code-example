from rest_framework import serializers

from limits.models import Limit


class LimitInfoSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = Limit
        fields = ('year', 'data')

    def get_data(self, limit):
        return limit.get_limit_data()
