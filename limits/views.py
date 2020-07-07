from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin

from limits.serializers import LimitInfoSerializer
from limits.models import Limit


class LimitRetrieveView(RetrieveModelMixin, GenericViewSet):
    queryset = Limit.objects.all().prefetch_related('models')
    serializer_class = LimitInfoSerializer
