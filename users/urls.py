from django.contrib import admin
from django.urls import path
from .views import Login, LogOut, UserActions,GetUsers

urlpatterns=[
    path('login/',Login.as_view()), # To  users Login
    path('logout/',LogOut.as_view()),
    path('useractions/',UserActions.as_view()),
    path('getUsers/',GetUsers.as_view())
]