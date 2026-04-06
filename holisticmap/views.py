from django.shortcuts import render
from .models import Executive, Company, Employee, Skill, EmployeeSkill, Role, RoleSkill
# Create your views here.

# dummy for testing
CURRENT_ROLE = 'executive'

def index(request):
    # default empty lists
    executives = []
    companies = []
    employees = []
    roles = []

    if CURRENT_ROLE == 'executive':
    # Executives see all companies they own and their employees
        companies = Company.objects.all()
        employees = Employee.objects.all()
        roles = Role.objects.all()

    elif CURRENT_ROLE == 'employee':
    # Employees see only their own record
        employees = Employee.objects.filter(id=1)  # placeholder
        companies = Company.objects.filter(id=employees.first().company.id) if employees.exists() else []
        roles = Role.objects.filter(company__id=employees.first().company.id) if employees.exists() else []

    return render(request, 'index.html', {
        'executives': executives,
        'companies': companies,
        'employees': employees,
        'roles': roles,
        'current_role': CURRENT_ROLE
    })