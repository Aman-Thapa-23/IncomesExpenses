from django.contrib import admin
from .models import Income, Source
# Register your models here.

class IncomeAdmin(admin.ModelAdmin): 
    list_display = ('amount', 'date', 'description', 'owner', 'source')
    search_fields = ['date', 'description', 'source']

    list_per_page = 5

admin.site.register(Income, IncomeAdmin)
admin.site.register(Source)
