from django.urls import path
from event.views import common as views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', views.CommonEventViewSet, basename='events')
urlpatterns = [
    path("regional/info/", views.EventRegionalDataApiView.as_view()),
]+ router.urls