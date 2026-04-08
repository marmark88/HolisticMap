from django.shortcuts import render, redirect, get_object_or_404
from .models import Executive, Company, Employee, Skill, EmployeeSkill, Role, RoleSkill, Employer
from .services import match_employee_to_role
# Create your views here.

# dummy for testing
CURRENT_ROLE = 'employee'
# pick first employee as sample view
EMPLOYEE_ID = 1 
# placeholder for first executive
EXECUTIVE_ID = 1
# placeholder for first employer
EMPLOYER_ID = 2

def index(request):
    if CURRENT_ROLE == 'executive':
        return redirect('executive_dashboard')
    elif CURRENT_ROLE == 'employee':
        return redirect('employee_dashboard')
    elif CURRENT_ROLE == 'employer':
        return redirect('employer_dashboard')
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

def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.delete() # cascades to delete all employees, employers, and roles
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

def remove_skill(request, skill_id):
    employee = get_object_or_404(Employee, id=EMPLOYEE_ID)

    # get the skill from the request URL
    skill = get_object_or_404(Skill, id=skill_id)

    # remove the skill
    employee.skills.remove(skill)

    return redirect('employee_dashboard')

def employer_dashboard(request):
    employer = get_object_or_404(Employer, id=EMPLOYER_ID)
    company = employer.company

    employees = Employee.objects.filter(company=company)
    roles = Role.objects.filter(company=company)

    return render(request, 'employer_dashboard.html', {
        'current_role': CURRENT_ROLE,
        'employer': employer,
        'company': company,
        'employees': employees,
        'roles': roles,
    })

def role_detail(request, role_id):
    role = get_object_or_404(Role, id=role_id)

    if CURRENT_ROLE == 'employee':
        employee = get_object_or_404(Employee, id=EMPLOYEE_ID)
        matches = match_employee_to_role(role.company, employee, role=role)
    else:
        matches = match_employee_to_role(role.company, role=role)

    return render(request, 'role_detail.html', {
        'CURRENT_ROLE': CURRENT_ROLE,
        'role': role,
        'matches': matches,
    })

# create a new role for a company
def create_role(request, company_id):
    # Executives or employers can create a new role for a company.
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        skills = request.POST.get('skills')

        if title and description:
            # Save the new role and assign to a variable
            role = Role.objects.create(company=company, title=title, description=description)
            
            # Add skills if provided
            if skills:
                skills_name = [s.strip() for s in skills.split(',') if s.strip()]
                for name in skills_name:
                    skill, created = Skill.objects.get_or_create(name=name)
                    RoleSkill.objects.create(role=role, skill=skill)
            
            # Redirect based on role
            if CURRENT_ROLE == 'executive':
                return redirect('executive_dashboard')
            else:
                return redirect('employer_dashboard')

    return render(request, 'create_role.html', {'company': company})

def delete_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    role.delete() # delete the role and all associated RoleSkills

    if CURRENT_ROLE == 'executive':
        return redirect('executive_dashboard')
    else:
        return redirect('employer_dashboard')
        