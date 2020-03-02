from django.contrib import admin
from django.urls import path
from creditManagement.views import *
urlpatterns=[
    path('creditManagement/',CreditManagement.as_view()),# To  users Login
    path('loadCredit/',LoadCredit.as_view()),
    #path('history/',History.as_view())
]