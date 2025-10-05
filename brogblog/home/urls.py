from django.urls import path

from . import views


urlpatterns = [
    # ex: /polls/
    path("", views.HomeView.as_view(), name="home"),
]