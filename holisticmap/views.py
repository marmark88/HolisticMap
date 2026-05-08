from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .models import (
    Executive,
    Company,
    Employee,
    Skill,
    EmployeeSkill,
    Role,
    RoleSkill,
    Employer,
    Education,
    RoleEducation,
    EmployeeEducation,
)
from .services import match_employee_to_role
from .forms import ExecutiveRegistrationForm, EmployerRegistrationForm, EmployeeRegistrationForm

# Role education requirements match employees on degree + major only (see services.match_employee_to_role).
# School is stored as a sentinel so rows stay unique without asking employers for institution.
ROLE_REQUIREMENT_EDUCATION_SCHOOL = "ANY"

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" aria-label="H">
  <rect width="32" height="32" rx="8" fill="#2563eb"/>
  <path fill="#fff" d="M9 8h3.5v6.25h7V8H23v16h-3.5v-6.25h-7V24H9V8z"/>
</svg>"""


def site_favicon(request):
    response = HttpResponse(FAVICON_SVG.strip(), content_type="image/svg+xml; charset=utf-8")
    response["Cache-Control"] = "public, max-age=86400"
    return response


def _get_user_role(user):
    if hasattr(user, 'executive'):
        return 'executive'
    if hasattr(user, 'employer'):
        return 'employer'
    if hasattr(user, 'employee'):
        return 'employee'
    return None


def _empty_role_draft(company_id):
    return {
        "company_id": company_id,
        "title": "",
        "description": "",
        "required_skills": [],
        "preferred_skills": [],
        "required_education": [],
        "preferred_education": [],
    }


def _get_role_draft(request, company_id):
    draft = request.session.get("role_draft")
    if not draft or draft.get("company_id") != company_id:
        draft = _empty_role_draft(company_id)
        request.session["role_draft"] = draft
        request.session.modified = True
    return draft


def _save_role_draft(request, draft):
    request.session["role_draft"] = draft
    request.session.modified = True


def _sync_role_draft_basics_from_post(request, draft):
    """Keep title/description in session when other forms POST (skills/education)."""
    if 'draft_title' in request.POST:
        draft["title"] = request.POST.get("draft_title", "").strip()
    if 'draft_description' in request.POST:
        draft["description"] = request.POST.get("draft_description", "").strip()
    if 'draft_title' in request.POST or 'draft_description' in request.POST:
        _save_role_draft(request, draft)


def _merge_skill_into_bucket(bucket, skill_name, min_years):
    key = skill_name.casefold()
    for entry in bucket:
        if entry["name"].casefold() == key:
            entry["name"] = skill_name
            entry["min_years"] = min_years
            return
    bucket.append({"name": skill_name, "min_years": min_years})


def _redirect_after_role_action(request, current_role):
    if current_role == "executive":
        return redirect("executive_dashboard")
    return redirect("employer_dashboard")


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
    employee_skills = EmployeeSkill.objects.filter(employee=employee).select_related('skill')
    employee_education = Education.objects.filter(
        employeeeducation__employee=employee
    ).distinct()

    role = _get_user_role(request.user)
    # Pass to template
    return render(request, 'employee_dashboard.html', {
        'current_role': 'employee',
        'employee': employee,
        'companies': companies,
        'roles': roles, # roles in the company
        'employee_skills': employee_skills,
        'employee_education': employee_education,
        'role': role, # user's current role
    })

@login_required
def add_skill(request):
    if not hasattr(request.user, 'employee'):
        return HttpResponseForbidden("Employee access required.")
    employee = request.user.employee

    # Handle adding a new skill
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name', '').strip()
        years_experience_raw = request.POST.get('years_experience', '0').strip()
        try:
            years_experience = int(years_experience_raw)
        except ValueError:
            years_experience = -1

        if skill_name and years_experience >= 0:
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            employee_skill, _ = EmployeeSkill.objects.get_or_create(
                employee=employee,
                skill=skill,
            )
            employee_skill.years_experience = years_experience
            employee_skill.save()
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
def add_education(request):
    if not hasattr(request.user, 'employee'):
        return HttpResponseForbidden("Employee access required.")
    employee = request.user.employee

    if request.method == 'POST':
        school = request.POST.get('school', '').strip()
        degree = request.POST.get('degree', '').strip()
        field_of_study = request.POST.get('field_of_study', '').strip()
        if school and degree and field_of_study:
            education, _ = Education.objects.get_or_create(
                school=school,
                degree=degree,
                field_of_study=field_of_study,
            )
            EmployeeEducation.objects.get_or_create(
                employee=employee,
                education=education,
            )
    return redirect('employee_dashboard')


@login_required
def remove_education(request, education_id):
    if not hasattr(request.user, 'employee'):
        return HttpResponseForbidden("Employee access required.")
    employee = request.user.employee
    education = get_object_or_404(Education, id=education_id)
    EmployeeEducation.objects.filter(
        employee=employee,
        education=education,
    ).delete()
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
    required_skills = role.roleskill_set.filter(is_required=True).select_related('skill')
    preferred_skills = role.roleskill_set.filter(is_required=False).select_related('skill')
    required_education = Education.objects.filter(
        roleeducation__role=role,
        roleeducation__is_required=True,
    ).distinct()
    preferred_education = Education.objects.filter(
        roleeducation__role=role,
        roleeducation__is_required=False,
    ).distinct()

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

    summary_matches = [
        {
            'employee': match['employee'],
            'score': match['score'],
        }
        for match in matches
    ]

    return render(request, 'role_detail.html', {
        'CURRENT_ROLE': current_role,
        'role': role,
        'matches': matches,
        'summary_matches': summary_matches,
        'required_skills': required_skills,
        'preferred_skills': preferred_skills,
        'required_education': required_education,
        'preferred_education': preferred_education,
    })


@login_required
def role_employee_match_detail(request, role_id, employee_id):
    role = get_object_or_404(Role, id=role_id)
    current_role = _get_user_role(request.user)
    if current_role == 'employer':
        if request.user.employer.company_id != role.company_id:
            return HttpResponseForbidden("Cannot view roles outside your company.")
    elif current_role == 'executive':
        if request.user.executive.id != role.company.executive_id:
            return HttpResponseForbidden("Cannot view roles outside your company.")
    else:
        return HttpResponseForbidden("Only employers and executives can view this page.")

    employee = get_object_or_404(Employee, id=employee_id, company=role.company)
    matches = match_employee_to_role(role.company, employee=employee, role=role)
    if not matches:
        return HttpResponseForbidden("No match data found for this employee.")

    return render(request, 'role_employee_match_detail.html', {
        'CURRENT_ROLE': current_role,
        'role': role,
        'employee': employee,
        'match': matches[0],
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

    if request.GET.get("cancel") == "1":
        request.session.pop("role_draft", None)
        return _redirect_after_role_action(request, current_role)

    draft = _get_role_draft(request, company_id)
    error = ""

    if request.method == 'POST':
        action = request.POST.get("action", "")
        _sync_role_draft_basics_from_post(request, draft)

        if action in (
            "add_required_skill",
            "add_preferred_skill",
        ):
            bucket_key = "required_skills" if action == "add_required_skill" else "preferred_skills"
            skill_name = request.POST.get("skill_name", "").strip()
            years_raw = request.POST.get("min_years_experience", "0").strip()
            try:
                min_years = int(years_raw)
            except ValueError:
                min_years = -1
            if skill_name and min_years >= 0:
                _merge_skill_into_bucket(draft[bucket_key], skill_name, min_years)
                _save_role_draft(request, draft)
            return redirect("create_role", company_id=company_id)

        if action in ("remove_required_skill", "remove_preferred_skill"):
            bucket_key = "required_skills" if action == "remove_required_skill" else "preferred_skills"
            try:
                idx = int(request.POST.get("index", "-1"))
            except ValueError:
                idx = -1
            if 0 <= idx < len(draft[bucket_key]):
                draft[bucket_key].pop(idx)
                _save_role_draft(request, draft)
            return redirect("create_role", company_id=company_id)

        if action in ("add_required_education", "add_preferred_education"):
            bucket_key = (
                "required_education" if action == "add_required_education" else "preferred_education"
            )
            degree = request.POST.get("degree", "").strip()
            field_of_study = request.POST.get("field_of_study", "").strip()
            if degree and field_of_study:
                draft[bucket_key].append({
                    "degree": degree,
                    "field_of_study": field_of_study,
                })
                _save_role_draft(request, draft)
            return redirect("create_role", company_id=company_id)

        if action in ("remove_required_education", "remove_preferred_education"):
            bucket_key = (
                "required_education" if action == "remove_required_education" else "preferred_education"
            )
            try:
                idx = int(request.POST.get("index", "-1"))
            except ValueError:
                idx = -1
            if 0 <= idx < len(draft[bucket_key]):
                draft[bucket_key].pop(idx)
                _save_role_draft(request, draft)
            return redirect("create_role", company_id=company_id)

        if action == "submit_role":
            title = request.POST.get("title", "").strip()
            description = request.POST.get("description", "").strip()
            draft["title"] = title
            draft["description"] = description
            _save_role_draft(request, draft)
            if not title or not description:
                error = "Enter a role title and description before submitting."
            else:
                role = Role.objects.create(company=company, title=title, description=description)

                for entry in draft["required_skills"]:
                    skill, _ = Skill.objects.get_or_create(name=entry["name"])
                    RoleSkill.objects.update_or_create(
                        role=role,
                        skill=skill,
                        is_required=True,
                        defaults={"min_years_experience": entry["min_years"]},
                    )

                for entry in draft["preferred_skills"]:
                    skill, _ = Skill.objects.get_or_create(name=entry["name"])
                    RoleSkill.objects.update_or_create(
                        role=role,
                        skill=skill,
                        is_required=False,
                        defaults={"min_years_experience": entry["min_years"]},
                    )

                for entry in draft["required_education"]:
                    education, _ = Education.objects.get_or_create(
                        school=ROLE_REQUIREMENT_EDUCATION_SCHOOL,
                        degree=entry["degree"],
                        field_of_study=entry["field_of_study"],
                    )
                    RoleEducation.objects.update_or_create(
                        role=role,
                        education=education,
                        defaults={"is_required": True},
                    )

                for entry in draft["preferred_education"]:
                    education, _ = Education.objects.get_or_create(
                        school=ROLE_REQUIREMENT_EDUCATION_SCHOOL,
                        degree=entry["degree"],
                        field_of_study=entry["field_of_study"],
                    )
                    if RoleEducation.objects.filter(role=role, education=education).exists():
                        continue
                    RoleEducation.objects.create(
                        role=role,
                        education=education,
                        is_required=False,
                    )

                request.session.pop("role_draft", None)
                return _redirect_after_role_action(request, current_role)

        return redirect("create_role", company_id=company_id)

    return render(request, 'create_role.html', {
        'company': company,
        'role': current_role,
        'draft': draft,
        'error': error,
    })

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
        