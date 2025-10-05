from django.urls import path

from . import views


urlpatterns = [
    # ex: /polls/
    path("", views.StudentView.as_view(), name="index"),
]