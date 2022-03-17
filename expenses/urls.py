from django.urls import path
from . import views

app_name='expense'

urlpatterns =[
    path('', views.index, name="expenses"),
    path('add-expenses/', views.add_expenses, name="add-expenses"),
    path('<int:id>/edit-expense/', views.edit_expense, name='edit-expense'),
    path('<int:id>/delete-expense/', views.delete_expense, name='delete-expense'),
]
