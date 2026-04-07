from .models import Role, Employee 

def match_employee_to_role(company, employee=None, role=None):
    """
    Return matches between employees and roles based on skill overlap score.
    
    - If role is provided → match employees to that one role
    - If employee is provided → match that employee to roles
    - Otherwise → match all employees to all roles
    """
    # handle roles
    if role:
        roles = [role]
    else:
        roles = Role.objects.filter(company=company).prefetch_related('skills')

    # if employee is provided, only match that employee to roles, otherwise match all employees to roles
    if employee:
        employees = [employee]
    else:
        employees = Employee.objects.filter(company=company).prefetch_related('skills')

    matches = []
    for role in roles:
        role_skills = set(role.skills.all())

        for employee in employees:
            employee_skills = set(employee.skills.all())

            if not role_skills:
                score = 0
            else:
                score = len(role_skills & employee_skills) / len(role_skills)
            
            matches.append({
                'role': role,
                'employee': employee,
                'score': round(score, 2),
            })
    
    # sort highest match first
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches