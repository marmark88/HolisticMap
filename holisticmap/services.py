from .models import Role, Employee 

def match_employee_to_role(company, employee=None):
    """
    Return a sorted list of matches between a specific employee and open roles (if employee is provided) 
    or all employees and roles based on skill overlap score. Build on this later to have more effecient search.
    Right now it is O(n^2) because it loops through all employees for each role.

    """

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