from rest_framework import serializers

from limits.models import Limit, Source, LimitArticle, LimitDateInfo


class LimitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Limit
        fields = '__all__'


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = '__all__'


class LimitArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = LimitArticle
        fields = '__all__'


class DateParamSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)


class LimitDateInfoSerializer(serializers.Serializer):

    class Meta:
        models = LimitDateInfo
        fields = '__all__'
