from django.urls import path
from .views import user_login, user_signup

urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('signup/', user_signup, name='user_signup'),
]
