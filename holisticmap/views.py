from django.shortcuts import render
from .models import Executive, Company, Employee
# Create your views here.
def index(request):
    executives = Executive.objects.all()
    companies = Company.objects.all()
    employees = Employee.objects.all()

    return render(request, 'index.html', {
        'executives': executives,
        'companies': companies,
        'employees': employees,
    })