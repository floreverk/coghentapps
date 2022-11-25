from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("querybuilder", views.buildquery),
    path("getldes", views.getldes),
    path("randomimage", views.image)
]