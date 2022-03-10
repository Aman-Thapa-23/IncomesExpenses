from django.urls import path
from . import views

app_name='expense'

urlpatterns =[
    path('', views.index, name="expenses"),
    path('add-expenses/', views.add_expenses, name="add-expenses"),
]
