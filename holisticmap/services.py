from .models import Role, Employee

def match_employee_to_role(company, employee=None, role=None):
    """
    Return matches between employees and roles based on skill + education overlap score.
    
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
        employees = Employee.objects.filter(company=company).prefetch_related(
            'employeeskill_set__skill',
            'employeeeducation_set__education',
        )

    matches = []
    for role in roles:
        role_skill_rows = role.roleskill_set.select_related('skill')
        role_education_rows = role.roleeducation_set.select_related('education')
        required_skill_map = {}
        preferred_skill_map = {}
        required_education_map = {}
        preferred_education_map = {}
        for role_skill in role_skill_rows:
            skill = role_skill.skill
            if not skill.name:
                continue
            key = skill.name.casefold()
            if role_skill.is_required:
                required_skill_map[key] = role_skill
            else:
                preferred_skill_map[key] = role_skill

        for role_education in role_education_rows:
            education = role_education.education
            key = (
                f"{education.degree}|{education.field_of_study}"
            ).casefold()
            if role_education.is_required:
                required_education_map[key] = education
            else:
                preferred_education_map[key] = education

        required_skill_keys = set(required_skill_map.keys())
        preferred_skill_keys = set(preferred_skill_map.keys())
        required_education_keys = set(required_education_map.keys())
        preferred_education_keys = set(preferred_education_map.keys())

        for employee in employees:
            employee_skill_map = {
                employee_skill.skill.name.casefold(): employee_skill
                for employee_skill in employee.employeeskill_set.all()
                if employee_skill.skill.name
            }
            employee_skill_keys = set(employee_skill_map.keys())
            employee_education_keys = {
                (
                    f"{employee_education.education.degree}|"
                    f"{employee_education.education.field_of_study}"
                ).casefold()
                for employee_education in employee.employeeeducation_set.all()
            }

            matching_required_keys = {
                key for key in required_skill_keys
                if key in employee_skill_map
                and employee_skill_map[key].years_experience >= required_skill_map[key].min_years_experience
            }
            matching_preferred_keys = {
                key for key in preferred_skill_keys
                if key in employee_skill_map
                and employee_skill_map[key].years_experience >= preferred_skill_map[key].min_years_experience
            }
            matching_required_education_keys = required_education_keys & employee_education_keys
            matching_preferred_education_keys = preferred_education_keys & employee_education_keys

            matching_skills = (
                {required_skill_map[key].skill for key in matching_required_keys}
                | {preferred_skill_map[key].skill for key in matching_preferred_keys}
            )
            matching_education = (
                {required_education_map[key] for key in matching_required_education_keys}
                | {preferred_education_map[key] for key in matching_preferred_education_keys}
            )
            missing_required_skill_details = []
            for key in required_skill_keys:
                role_skill = required_skill_map[key]
                employee_skill = employee_skill_map.get(key)
                if employee_skill is None:
                    missing_required_skill_details.append({
                        'skill': role_skill.skill,
                        'required_years': role_skill.min_years_experience,
                        'employee_years': None,
                    })
                elif employee_skill.years_experience < role_skill.min_years_experience:
                    missing_required_skill_details.append({
                        'skill': role_skill.skill,
                        'required_years': role_skill.min_years_experience,
                        'employee_years': employee_skill.years_experience,
                    })

            missing_preferred_skill_details = []
            for key in preferred_skill_keys:
                role_skill = preferred_skill_map[key]
                employee_skill = employee_skill_map.get(key)
                if employee_skill is None:
                    missing_preferred_skill_details.append({
                        'skill': role_skill.skill,
                        'required_years': role_skill.min_years_experience,
                        'employee_years': None,
                    })
                elif employee_skill.years_experience < role_skill.min_years_experience:
                    missing_preferred_skill_details.append({
                        'skill': role_skill.skill,
                        'required_years': role_skill.min_years_experience,
                        'employee_years': employee_skill.years_experience,
                    })
            missing_required_education = {
                required_education_map[key]
                for key in (required_education_keys - employee_education_keys)
            }
            missing_preferred_education = {
                preferred_education_map[key]
                for key in (preferred_education_keys - employee_education_keys)
            }

            # Required criteria count more than preferred criteria.
            weighted_total = (
                (len(required_skill_keys) * 1.0)
                + (len(preferred_skill_keys) * 0.5)
                + (len(required_education_keys) * 1.0)
                + (len(preferred_education_keys) * 0.5)
            )
            weighted_matches = (
                (len(matching_required_keys) * 1.0)
                + (len(matching_preferred_keys) * 0.5)
                + (len(matching_required_education_keys) * 1.0)
                + (len(matching_preferred_education_keys) * 0.5)
            )

            if weighted_total == 0:
                score = 0
            else:
                score = (weighted_matches / weighted_total) * 100
            
            matches.append({
                'role': role,
                'employee': employee,
                'matching_skills': matching_skills,
                'matching_required_skills': [
                    {
                        'skill': required_skill_map[key].skill,
                        'required_years': required_skill_map[key].min_years_experience,
                        'employee_years': employee_skill_map[key].years_experience,
                    }
                    for key in matching_required_keys
                ],
                'matching_preferred_skills': [
                    {
                        'skill': preferred_skill_map[key].skill,
                        'required_years': preferred_skill_map[key].min_years_experience,
                        'employee_years': employee_skill_map[key].years_experience,
                    }
                    for key in matching_preferred_keys
                ],
                'matching_education': matching_education,
                'matching_required_education': {
                    required_education_map[key] for key in matching_required_education_keys
                },
                'matching_preferred_education': {
                    preferred_education_map[key] for key in matching_preferred_education_keys
                },
                'missing_required_skills': missing_required_skill_details,
                'missing_preferred_skills': missing_preferred_skill_details,
                'missing_required_education': missing_required_education,
                'missing_preferred_education': missing_preferred_education,
                'score': round(score, 2),
            })
    
    # sort highest match first
    matches.sort(key=lambda x: x['score'], reverse=True)

    return matches