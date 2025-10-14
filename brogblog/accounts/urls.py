from django.urls import path

from accounts.views import *


urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('my-account/', MyAccountView.as_view(), name='my-account'),
]