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
        role_skill_map = {
            skill.name.casefold(): skill
            for skill in role.skills.all()
            if skill.name
        }
        role_skill_keys = set(role_skill_map.keys())

        for employee in employees:
            employee_skill_keys = {
                skill.name.casefold()
                for skill in employee.skills.all()
                if skill.name
            }

            matching_skills_keys = role_skill_keys & employee_skill_keys
            matching_skills = {role_skill_map[key] for key in matching_skills_keys}
            missing_skills = {role_skill_map[key] for key in (role_skill_keys - employee_skill_keys)}

            if not role_skill_keys:
                score = 0
            else:
                score = (len(matching_skills_keys) / len(role_skill_keys)) * 100
            
            matches.append({
                'role': role,
                'employee': employee,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'score': round(score, 2),
            })
    
    # sort highest match first
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches