from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from userpreferences.models import UserPreference
from django.contrib import messages
from django.core.paginator import Paginator
import json


# Create your views here.

def search_expenses(request):
    if request.method == "POST":        
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(amount__startswith=search_str, owner=request.user) | Expense.objects.filter(
            date__startswith=search_str, owner=request.user) | Expense.objects.filter(description__icontains=search_str, owner=request.user) | Expense.objects.filter(category__icontains=search_str, owner=request.user)
        
        data = expenses.values()
  
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user= request.user).currency

    context = {'expenses': expenses, 'page_obj': page_obj, 'currency':currency }
    return render(request, 'expenses/index.html', context)


def add_expenses(request):
    categories = Category.objects.all()
    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense-date']

        context = {'categories': categories, 'values': request.POST}

        if not amount:
            messages.error(request, 'Amount is needed.')
            return render(request, 'expenses/add_expenses.html', context)
        if not description:
            messages.error(request, 'Description is needed.')
            return render(request, 'expenses/add_expenses.html', context)
        if not category:
            messages.error(request, 'Category is needed.')
            return render(request, 'expenses/add_expenses.html', context)
        if not date:
            messages.error(request, 'Date is needed.')
            return render(request, 'expenses/add_expenses.html', context)

        Expense.objects.create(owner=request.user, amount=amount,
                               description=description, category=category, date=date)
        messages.success(request, 'Expense added successfully.')
        return redirect('expense:expenses')

    else:
        context = {'categories': categories, 'values': request.POST}
        return render(request, 'expenses/add_expenses.html', context)


def edit_expense(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {'expense': expense, 'categories': categories, 'values': expense}
    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        date = request.POST['expense-date']

        if not amount:
            messages.error(request, 'Amount is needed.')
            return render(request, 'expenses/edit_expense.html', context)
        if not description:
            messages.error(request, 'Description is needed.')
            return render(request, 'expenses/edit_expense.html', context)
        if not category:
            messages.error(request, 'Category is needed.')
            return render(request, 'expenses/edit_expense.html', context)
        if not date:
            messages.error(request, 'Date is needed.')
            return render(request, 'expenses/edit_expense.html', context)

        expense.amount = amount
        expense.description = description
        expense.category = category
        expense.data = date
        expense.save()
        messages.success(request, "Expense is updated.")

        return redirect('expense:expenses')

    return render(request, 'expenses/edit_expense.html', context)


def delete_expense(request, id):
    expense = get_object_or_404(Expense, pk=id)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense is deleted.")
        return redirect('expense:expenses')
    context = {'expense': expense}
    return render(request, 'expenses/delete_expense.html', context)
