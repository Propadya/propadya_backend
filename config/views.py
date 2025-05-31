from django.shortcuts import render
from django.conf import settings


def home(request):
    return render(request, "index.html", {"FRONTEND_URL": settings.FRONTEND_URL,
                                          "debug": settings.DEBUG
                                          })

