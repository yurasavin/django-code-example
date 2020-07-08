from django.db import models
from django.db.models import Case, Sum, When
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from contracts.models import Contract
from contracts.serializers import ContractSerializer

from core.viewset_mixins import SerializerMapMixin

from limits.models import Limit, LimitDateInfo, Source
from limits.serializers import (DateParamSerializer, LimitDateInfoSerializer,
                                LimitSerializer, SourceSerializer)

from tenders.models import Tender
from tenders.serializers import TenderSerializer


class LimitViewSet(ModelViewSet):
    queryset = Limit.objects.all()
    serializer_class = LimitSerializer

    @action(detail=True)
    def latest_date_info(self, request, pk=None):
        queryset = LimitDateInfo.objects.order_by('-date')[:1]
        return self._date_response(queryset, pk)

    @action(detail=True)
    def date_info(self, request, pk=None):
        date = self._get_date_param()
        queryset = LimitDateInfo.objects.filter(date=date)
        return self._date_response(queryset, pk)

    def _date_response(self, queryset, pk):
        limit_info = get_object_or_404(queryset, limit_id=pk)
        serializer = LimitDateInfoSerializer(limit_info)
        return Response(serializer.data)

    def _get_date_param(self):
        """
        Validate and return date param from query params
        """
        date = self.request.query_params.get('date')
        serializer = DateParamSerializer(data={'date': date})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['date']


class SourceViewSet(SerializerMapMixin, ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    serializer_class_map = {
        'contracts': ContractSerializer,
        'tenders': TenderSerializer,
    }

    @action(detail=True)
    def contracts(self, request, pk=None):
        limit = self.get_object()
        contracts = self._get_contracts(limit)
        serializer = self.get_serializer(contracts, many=True)
        return Response(serializer.data)

    def _get_contracts(self):
        """
        Return contracts with amount
        """
        return Contract.objects.filter(
            contractprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
        ).annotate(
            money=Case(
                When(
                    contractprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
                    then=Sum('contractprice__money', distinct=True),
                ),
                output_field=models.DecimalField(),
            ),
            delta=Case(
                When(
                    contractprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
                    then=Sum(
                        'contractprice__contractpricechange__delta',
                        distinct=True,
                    ),
                ),
                output_field=models.DecimalField(),
            ),
        )

    @action(detail=True)
    def tenders(self, request, pk=None):
        limit = self.get_object()
        tenders = self._tenders_in_work(limit)
        serializer = self.get_serializer(tenders, many=True)
        return Response(serializer.data)

    def _tenders_in_work(self):
        """
        Return tenders in process with amount
        """
        return Tender.objects.filter(
            status='in_work',
            startprice__limit__industry_code__limit_article__source_id=self.id,
        ).annotate(
            money=Case(
                When(
                    startprice__limit__industry_code__limit_article__source_id=self.id,  # noqa: E501
                    then=Sum('startprice__money'),
                ),
                output_field=models.DecimalField(),
            ),
        )
