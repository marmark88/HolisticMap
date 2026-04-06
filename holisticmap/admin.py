from django.contrib import admin
from .models import Executive, Company, Employee, Skill, EmployeeSkill, Role, RoleSkill
# Register your models here.

admin.site.register(Executive)
admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(Skill)
admin.site.register(EmployeeSkill)
admin.site.register(Role)
admin.site.register(RoleSkill)