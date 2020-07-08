from django.urls import include, path

from rest_framework.routers import DefaultRouter

from limits import views

router = DefaultRouter()
router.register(r'limits', views.LimitViewSet)
router.register(r'sources', views.SourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
