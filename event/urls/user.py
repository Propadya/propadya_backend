from django.urls import path
from event.views import user as views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', views.EventViewSet, basename='events')
urlpatterns = [
]+ router.urls
