from django.urls import path, include


urlpatterns = [
    path("user/", include("event.urls.user")),
    path("public/", include("event.urls.common")),
]
