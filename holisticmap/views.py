from django.shortcuts import render, redirect
from .models import Executive, Company, Employee, Skill, EmployeeSkill, Role, RoleSkill
# Create your views here.

# dummy for testing
CURRENT_ROLE = 'employee'
# pick first employee as sample view
EMPLOYEE_ID = 1 

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
        employee = Employee.objects.get(id=EMPLOYEE_ID)
        companies = [employee.company]
        roles = Role.objects.filter(company=employee.company)
        
        # Employee skills
        employee_skills = employee.skills.all()

        # Handle adding a new skill
        if request.method == 'POST':
            skill_name = request.POST.get('skill_name')
            if skill_name:
                skill, created = Skill.objects.get_or_create(name=skill_name)
                employee.skills.add(skill)  # ManyToMany prevents duplicates automatically
                return redirect('index')
        
        # Pass to template
        context = {
            'current_role': CURRENT_ROLE,
            'employee': employee,
            'companies': companies,
            'roles': roles,
            'employee_skills': employee_skills,
        }
        return render(request, 'index.html', context)

    return render(request, 'index.html', {
        'executives': executives,
        'companies': companies,
        'employees': employees,
        'roles': roles,
        'current_role': CURRENT_ROLE
    })