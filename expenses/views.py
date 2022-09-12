from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from userpreferences.models import UserPreference
from django.contrib import messages
from django.core.paginator import Paginator
import json
import datetime
import csv
import xlwt

from django.template.loader import render_to_string
# from weasyprint import HTML
import tempfile
from django.db.models import Sum


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
    # categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency

    context = {'expenses': expenses,
               'page_obj': page_obj, 'currency': currency}
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
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


@login_required(login_url='/authentication/login')
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


@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = get_object_or_404(Expense, pk=id)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense is deleted.")
        return redirect('expense:expenses')
    context = {'expense': expense}
    return render(request, 'expenses/delete_expense.html', context)


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(
        owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category

    # set remove duplicate objects given by map and list will help to work easily
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filter_by_category = expenses.filter(category=category)

        for item in filter_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename= Expenses' + \
        str(datetime.datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description,
                         expense.category, expense.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename= Expenses' + \
        str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')  # workbook
    ws = wb.add_sheet('Expenses')  # workSheet
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response


# def export_pdf(request):
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename= Expenses' + \
#         str(datetime.datetime.now())+'.pdf'

#     response['Content-Transfer-Encoding'] = 'binary'

#     html_string = render_to_string('expenses/pdf-output.html', {'expenses':[], 'total':0})
#     html = HTML(string=html_string)

#     result = html.write_pdf()

#     with tempfile.NamedTemporaryFile(delete=True) as output:
#         output.write(result)
#         output.flush()

#         output= open(output.name, 'rb')
#         response.write(output.read())

#     return response