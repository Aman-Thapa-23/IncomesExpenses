from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name='income'

urlpatterns =[
    path('', views.index, name="incomes"), 
    path('add-incomes', views.add_incomes, name="add-incomes"),
    path('<int:id>/edit-income', views.edit_income, name='edit-income'),
    path('<int:id>/delete-income', views.delete_income, name='delete-income'),
    path('search-incomes', csrf_exempt(views.search_incomes), name='search-incomes'),
    path('income-source-summary', views.income_source_summary, name='income-source-summary'),
    path('income-stats', views.stats_view, name='income-stats'),
]
