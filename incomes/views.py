from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Income, Source
from userpreferences.models import UserPreference
from django.contrib import messages
from django.core.paginator import Paginator
import json

# Create your views here.

def search_incomes(request):
    if request.method == "POST":        
        search_str = json.loads(request.body).get('searchText')
        incomes = Income.objects.filter(amount__startswith=search_str, owner=request.user) | Income.objects.filter(
            date__startswith=search_str, owner=request.user) | Income.objects.filter(description__icontains=search_str, owner=request.user) | Income.objects.filter(source__icontains=search_str, owner=request.user)
        
        data = incomes.values()
  
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user= request.user).currency

    context = {'income': income, 'page_obj': page_obj, 'currency':currency }
    return render(request, 'incomes/index.html', context)


def add_incomes(request):
    sources = Source.objects.all()
    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        source = request.POST['source']
        date = request.POST['income-date']

        context = {'sources': sources, 'values': request.POST}

        if not amount:
            messages.error(request, 'Amount is needed.')
            return render(request, 'incomes/add_incomes.html', context)
        if not description:
            messages.error(request, 'Description is needed.')
            return render(request, 'incomes/add_incomes.html', context)
        if not source:
            messages.error(request, 'Source is needed.')
            return render(request, 'incomes/add_incomes.html', context)
        if not date:
            messages.error(request, 'Date is needed.')
            return render(request, 'incomes/add_incomes.html', context)

        Income.objects.create(owner=request.user, amount=amount,
                               description=description, source=source, date=date)
        messages.success(request, 'Income added successfully.')
        return redirect('income:incomes')

    else:
        context = {'sources': sources, 'values': request.POST}
        return render(request, 'incomes/add_incomes.html', context)


def edit_income(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {'income': income, 'sources': sources, 'values': income}
    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        source = request.POST['source']
        date = request.POST['income-date']

        if not amount:
            messages.error(request, 'Amount is needed.')
            return render(request, 'incomes/edit_income.html', context)
        if not description:
            messages.error(request, 'Description is needed.')
            return render(request, 'incomes/edit_income.html', context)
        if not source:
            messages.error(request, 'Source is needed.')
            return render(request, 'incomes/edit_income.html', context)
        if not date:
            messages.error(request, 'Date is needed.')
            return render(request, 'incomes/edit_income.html', context)

        income.amount = amount
        income.description = description
        income.source = source
        income.data = date
        income.save()
        messages.success(request, "Expense is updated.")

        return redirect('income:incomes')

    return render(request, 'incomes/edit_income.html', context)


def delete_income(request, id):
    income = get_object_or_404(Income, pk=id)
    if request.method == "POST":
        income.delete()
        messages.success(request, "Income is deleted.")
        return redirect('income:incomes')
    context = {'income': income}
    return render(request, 'incomes/delete_income.html', context)