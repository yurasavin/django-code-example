from django.db import models
from django.db.models import Case, Sum, Q, When
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
        limit_info = LimitDateInfo.objects\
            .filter(limit_id=pk).order_by('date').last()
        return self._date_response(limit_info)

    @action(detail=True)
    def date_info(self, request, pk=None):
        date = self._get_date_param()
        queryset = LimitDateInfo.objects.all()
        limit_info = get_object_or_404(queryset, date=date, limit_id=pk)
        return self._date_response(limit_info)

    def _date_response(self, limit_info):
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
        source = self.get_object()
        contracts = self._get_contracts(source)
        serializer = self.get_serializer(contracts, many=True)
        return Response(serializer.data)

    def _get_contracts(self, source):
        """
        Return contracts with amount
        """
        source_id_equal = Q(contractprice__limit__industry_code__limit_article__source_id=source.id)  # noqa: E501
        return source.contracts.annotate(
            money=Case(
                When(
                    source_id_equal,
                    then=Sum('contractprice__money', distinct=True),
                ),
                output_field=models.DecimalField(),
            ),
            delta=Case(
                When(
                    source_id_equal,
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

    def _tenders_in_work(self, source):
        """
        Return tenders in process with amount
        """
        source_id_equal = Q(startprice__limit__industry_code__limit_article__source_id=source.id)  # noqa: E501
        return source.tenders\
            .filter(status='in_work')\
            .annotate(
                money=Case(
                    When(source_id_equal, then=Sum('startprice__money')),
                    output_field=models.DecimalField(),
                ),
            )
