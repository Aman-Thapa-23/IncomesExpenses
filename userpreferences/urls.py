from unicodedata import name
from django.urls import path
from . import views

app_name= 'userprefer'

urlpatterns = [
    path('', views.index, name='preferences'),
]