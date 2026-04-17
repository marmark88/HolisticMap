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
        roles = Role.objects.filter(company=company).prefetch_related('roleskill_set__skill')

    # if employee is provided, only match that employee to roles, otherwise match all employees to roles
    if employee:
        employees = [employee]
    else:
        employees = Employee.objects.filter(company=company).prefetch_related('skills')

    matches = []
    for role in roles:
        role_skill_rows = role.roleskill_set.select_related('skill')
        required_skill_map = {}
        preferred_skill_map = {}
        for role_skill in role_skill_rows:
            skill = role_skill.skill
            if not skill.name:
                continue
            key = skill.name.casefold()
            if role_skill.is_required:
                required_skill_map[key] = skill
            else:
                preferred_skill_map[key] = skill

        required_skill_keys = set(required_skill_map.keys())
        preferred_skill_keys = set(preferred_skill_map.keys())

        for employee in employees:
            employee_skill_keys = {
                skill.name.casefold()
                for skill in employee.skills.all()
                if skill.name
            }

            matching_required_keys = required_skill_keys & employee_skill_keys
            matching_preferred_keys = preferred_skill_keys & employee_skill_keys

            matching_skills = (
                {required_skill_map[key] for key in matching_required_keys}
                | {preferred_skill_map[key] for key in matching_preferred_keys}
            )
            missing_required_skills = {
                required_skill_map[key]
                for key in (required_skill_keys - employee_skill_keys)
            }
            missing_preferred_skills = {
                preferred_skill_map[key]
                for key in (preferred_skill_keys - employee_skill_keys)
            }

            # Required skills count more than preferred.
            weighted_total = (len(required_skill_keys) * 1.0) + (len(preferred_skill_keys) * 0.5)
            weighted_matches = (len(matching_required_keys) * 1.0) + (len(matching_preferred_keys) * 0.5)

            if weighted_total == 0:
                score = 0
            else:
                score = (weighted_matches / weighted_total) * 100
            
            matches.append({
                'role': role,
                'employee': employee,
                'matching_skills': matching_skills,
                'matching_required_skills': {required_skill_map[key] for key in matching_required_keys},
                'matching_preferred_skills': {preferred_skill_map[key] for key in matching_preferred_keys},
                'missing_required_skills': missing_required_skills,
                'missing_preferred_skills': missing_preferred_skills,
                'score': round(score, 2),
            })
    
    # sort highest match first
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches