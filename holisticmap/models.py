from django.db import models

# Create your models here.
class Executive (models.Model):
    name = models.CharField(max_length=255) # name of executive
    phone = models.CharField(max_length=255) # phone number
    created_at = models.DateTimeField(auto_now_add=True) # when account was created

    def __str__(self):
        return self.name

class Company (models.Model):
    executive = models.ForeignKey(Executive, on_delete=models.CASCADE) # executive's company
    name = models.CharField(max_length=255) # name of company
    employee_secret_hash = models.CharField(max_length=255) # company password for employees
    employer_secret_hash = models.CharField(max_length=255) # company password for employers
    company_size = models.IntegerField() # how many employees company has
    address = models.CharField(max_length=255) # address
    created_at = models.DateTimeField(auto_now_add=True) # when company was created in system

    def __str__(self):
        return self.name

class Skill (models.Model):
    name = models.CharField(max_length=255) # name of skill

    def __str__(self):
        return self.name

class Employee (models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE) # company employee works for
    name = models.CharField(max_length=255) # employee name
    phone = models.CharField(max_length=255) # phone number
    skills = models.ManyToManyField(Skill, through='EmployeeSkill') # what skills the employee has
    created_at = models.DateTimeField(auto_now_add=True) # when employee account was created

    def __str__(self):
        return self.name

class EmployeeSkill (models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE) # employee name
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE) # skill employee possesses

    class Meta:
        unique_together = ('employee', 'skill') # prevents duplicate skills assigned to one employee

class Employer (models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE) # company employer works for
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True) # when employer account was created

    def __str__(self):
        return self.name

class Role (models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE) # company name
    title = models.CharField(max_length=255) # title of open position
    description = models.TextField() # description of the role
    skills = models.ManyToManyField(Skill, through='RoleSkill') # skills required for position
    created_at = models.DateTimeField(auto_now_add=True) # when role was posted

    def __str__(self):
        return self.title

class RoleSkill (models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE) # role title
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE) # skills required for role

    class Meta:
        unique_together = ('role', 'skill') # prevents duplicate skills assigned to one role