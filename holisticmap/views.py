from django.shortcuts import render, redirect, get_object_or_404
from .models import Executive, Company, Employee, Skill, EmployeeSkill, Role, RoleSkill
# Create your views here.

# dummy for testing
CURRENT_ROLE = 'employee'
# pick first employee as sample view
EMPLOYEE_ID = 1 
# placeholder for first executive
EXECUTIVE_ID = 1

def index(request):
    if CURRENT_ROLE == 'executive':
        return redirect('executive_dashboard')
    elif CURRENT_ROLE == 'employee':
        return redirect('employee_dashboard')
    return redirect('index')  # default fallback

def executive_dashboard(request):
    # Executives see all companies they own, their employees, and open roles
    executive = get_object_or_404(Executive, id=EXECUTIVE_ID)
    companies = Company.objects.filter(executive=executive)
    employees = Employee.objects.filter(company__executive=executive)
    roles = Role.objects.filter(company__executive=executive)

    return render(request, 'executive_dashboard.html', {
        'current_role': CURRENT_ROLE,
        'executive': executive,
        'companies': companies,
        'employees': employees,
        'roles': roles,
    })  

def create_company(request):
    executive = get_object_or_404(Executive, id=EXECUTIVE_ID)

    # handle adding a new company
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        size = request.POST.get('company_size')
        secret = request.POST.get('join_secret')

        if name and address and size and secret:
            Company.objects.create(
                executive=executive,
                name=name,
                address=address,
                company_size=int(size),
                join_secret_hash=secret  # hash it in later version
            )
    return redirect('executive_dashboard')

def employee_dashboard(request):
    # Employees see only their own record
    employee = get_object_or_404(Employee, id=EMPLOYEE_ID)
    companies = [employee.company]
    roles = Role.objects.filter(company=employee.company)
        
    # Employee skills
    employee_skills = employee.skills.all() 

    # Pass to template
    return render(request, 'employee_dashboard.html', {
        'current_role': CURRENT_ROLE,
        'employee': employee,
        'companies': companies,
        'roles': roles,
        'employee_skills': employee_skills,
    })

def add_skill(request):
    employee = get_object_or_404(Employee, id=EMPLOYEE_ID)

    # Handle adding a new skill
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        if skill_name:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            employee.skills.add(skill)  # ManyToMany prevents duplicates automatically
    return redirect('employee_dashboard')