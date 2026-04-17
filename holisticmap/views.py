from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Executive, Company, Employee, Skill, EmployeeSkill, Role, RoleSkill, Employer
from .services import match_employee_to_role
from .forms import ExecutiveRegistrationForm, EmployerRegistrationForm, EmployeeRegistrationForm

def _get_user_role(user):
    if hasattr(user, 'executive'):
        return 'executive'
    if hasattr(user, 'employer'):
        return 'employer'
    if hasattr(user, 'employee'):
        return 'employee'
    return None


def index(request):
    if request.user.is_authenticated:
        role = _get_user_role(request.user)
        if role == 'executive':
            return redirect('executive_dashboard')
        if role == 'employer':
            return redirect('employer_dashboard')
        if role == 'employee':
            return redirect('employee_dashboard')
    return render(request, 'index.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            role = _get_user_role(user)
            if role == 'executive':
                return redirect('executive_dashboard')
            elif role == 'employer':
                return redirect('employer_dashboard')
            elif role == 'employee':
                return redirect('employee_dashboard')
            return redirect('login')
        else:
            error = "Invalid username or password"
            return render(request, 'login.html', {'error': error})
    return render(request, 'login.html')

# --- Logout ---

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def register_executive(request):
    if request.method == 'POST':
        form = ExecutiveRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Executive.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone']
            )
            return redirect('login')
    else:
        form = ExecutiveRegistrationForm()
    return render(request, 'register_executive', {'form': form})

def register_employer(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']
            secret = form.cleaned_data['company_secret']

            if not check_password(secret, company.employer_secret_hash):
                form.add_error('company_secret', 'Invalid employer secret')
            else:
                user = form.save()
                Employer.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    phone=form.cleaned_data['phone'],
                    company=company
                )
                return redirect('login')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'register_employer', {'form': form})

def register_employee(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']
            secret = form.cleaned_data['company_secret']

            if not check_password(secret, company.employee_secret_hash):
                form.add_error('company_secret', 'Invalid employee secret')
            else:
                user = form.save()
                Employee.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    phone=form.cleaned_data['phone'],
                    company=company
                )
                return redirect('login')
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'register_employee', {'form': form})

@login_required
def executive_dashboard(request):
    if not hasattr(request.user, 'executive'):
        return HttpResponseForbidden("Executive access required.")

    executive = request.user.executive
    companies = Company.objects.filter(executive=executive)
    employees = Employee.objects.filter(company__executive=executive)
    roles = Role.objects.filter(company__executive=executive)

    role = _get_user_role(request.user)

    return render(request, 'executive_dashboard.html', {
        'current_role': 'executive',
        'executive': executive,
        'companies': companies,
        'employees': employees,
        'roles': roles, # roles in the company
        'role': role, # user's current role
    })  

@login_required
def create_company(request):
    if not hasattr(request.user, 'executive'):
        return HttpResponseForbidden("Executive access required.")

    executive = request.user.executive

    # handle adding a new company
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        size = request.POST.get('company_size')
        employee_secret = request.POST.get('employee_secret')
        employer_secret = request.POST.get('employer_secret')

        if name and address and size and employee_secret and employer_secret:
            # hashes the shared password to make an account for employees and employers
            employee_secret_hash = make_password(employee_secret)
            employer_secret_hash = make_password(employer_secret)

            Company.objects.create(
                executive=executive,
                name=name,
                address=address,
                company_size=int(size),
                employee_secret_hash=employee_secret_hash,
                employer_secret_hash=employer_secret_hash,
            )
    return redirect('executive_dashboard')

@login_required
def delete_company(request, company_id):
    if not hasattr(request.user, 'executive'):
        return HttpResponseForbidden("Executive access required.")

    company = get_object_or_404(Company, id=company_id)
    if company.executive != request.user.executive:
        return HttpResponseForbidden("Cannot delete another executive's company.")
    company.delete() # cascades to delete all employees, employers, and roles
    return redirect('executive_dashboard')

@login_required
def employee_dashboard(request):
    if not hasattr(request.user, 'employee'):
        return HttpResponseForbidden("Employee access required.")

    employee = request.user.employee
    companies = [employee.company]
    roles = Role.objects.filter(company=employee.company)
        
    # Employee skills
    employee_skills = employee.skills.all() 

    role = _get_user_role(request.user)
    # Pass to template
    return render(request, 'employee_dashboard.html', {
        'current_role': 'employee',
        'employee': employee,
        'companies': companies,
        'roles': roles, # roles in the company
        'employee_skills': employee_skills,
        'role': role, # user's current role
    })

@login_required
def add_skill(request):
    if not hasattr(request.user, 'employee'):
        return HttpResponseForbidden("Employee access required.")
    employee = request.user.employee

    # Handle adding a new skill
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name')
        if skill_name:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            employee.skills.add(skill)  # ManyToMany prevents duplicates automatically
    return redirect('employee_dashboard')

@login_required
def remove_skill(request, skill_id):
    if not hasattr(request.user, 'employee'):
        return HttpResponseForbidden("Employee access required.")
    employee = request.user.employee

    # get the skill from the request URL
    skill = get_object_or_404(Skill, id=skill_id)

    # remove the skill
    employee.skills.remove(skill)

    return redirect('employee_dashboard')

@login_required
def employer_dashboard(request):
    if not hasattr(request.user, 'employer'):
        return HttpResponseForbidden("Employer access required.")

    employer = request.user.employer
    company = employer.company

    employees = Employee.objects.filter(company=company)
    roles = Role.objects.filter(company=company)

    role = _get_user_role(request.user)

    return render(request, 'employer_dashboard.html', {
        'current_role': 'employer',
        'employer': employer,
        'company': company,
        'employees': employees,
        'roles': roles, # roles in the company
        'role': role, # user's current role
    })

@login_required
def role_detail(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    current_role = _get_user_role(request.user)
    required_skills = role.skills.filter(roleskill__is_required=True).distinct()
    preferred_skills = role.skills.filter(roleskill__is_required=False).distinct()

    if current_role == 'employee':
        employee = request.user.employee
        if employee.company_id != role.company_id:
            return HttpResponseForbidden("Cannot view roles outside your company.")
        matches = match_employee_to_role(role.company, employee, role=role)
    elif current_role == 'employer':
        if request.user.employer.company_id != role.company_id:
            return HttpResponseForbidden("Cannot view roles outside your company.")
        matches = match_employee_to_role(role.company, role=role)
    elif current_role == 'executive':
        if request.user.executive.id != role.company.executive_id:
            return HttpResponseForbidden("Cannot view roles outside your company.")
        matches = match_employee_to_role(role.company, role=role)
    else:
        return HttpResponseForbidden("No valid role assigned.")

    return render(request, 'role_detail.html', {
        'CURRENT_ROLE': current_role,
        'role': role,
        'matches': matches,
        'required_skills': required_skills,
        'preferred_skills': preferred_skills,
    })

# create a new role for a company
@login_required
def create_role(request, company_id):
    current_role = _get_user_role(request.user)
    if current_role not in ('executive', 'employer'):
        return HttpResponseForbidden("Only executives and employers can create roles.")

    company = get_object_or_404(Company, id=company_id)
    if current_role == 'executive' and company.executive_id != request.user.executive.id:
        return HttpResponseForbidden("Cannot create role for another executive's company.")
    if current_role == 'employer' and company.id != request.user.employer.company_id:
        return HttpResponseForbidden("Cannot create role for another employer's company.")

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        required_skills = request.POST.get('required_skills', '')
        preferred_skills = request.POST.get('preferred_skills', '')

        if title and description:
            # Save the new role and assign to a variable
            role = Role.objects.create(company=company, title=title, description=description)
            
            # Add required and preferred skills if provided.
            # If a skill appears in both lists, required takes precedence.
            required_skill_names = {
                s.strip() for s in required_skills.split(',') if s.strip()
            }
            preferred_skill_names = {
                s.strip() for s in preferred_skills.split(',') if s.strip()
            } - required_skill_names

            for name in required_skill_names:
                skill, _ = Skill.objects.get_or_create(name=name)
                RoleSkill.objects.create(role=role, skill=skill, is_required=True)

            for name in preferred_skill_names:
                skill, _ = Skill.objects.get_or_create(name=name)
                RoleSkill.objects.create(role=role, skill=skill, is_required=False)
            
            if current_role == 'executive':
                return redirect('executive_dashboard')
            else:
                return redirect('employer_dashboard')

    return render(request, 'create_role.html', {'company': company})

@login_required
def delete_role(request, role_id):
    current_role = _get_user_role(request.user)
    if current_role not in ('executive', 'employer'):
        return HttpResponseForbidden("Only executives and employers can delete roles.")

    role = get_object_or_404(Role, id=role_id)
    if current_role == 'executive' and role.company.executive_id != request.user.executive.id:
        return HttpResponseForbidden("Cannot delete roles for another executive's company.")
    if current_role == 'employer' and role.company_id != request.user.employer.company_id:
        return HttpResponseForbidden("Cannot delete roles for another employer's company.")
    role.delete() # delete the role and all associated RoleSkills

    if current_role == 'executive':
        return redirect('executive_dashboard')
    else:
        return redirect('employer_dashboard')
        