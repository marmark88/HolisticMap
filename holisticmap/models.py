from django.contrib.auth.models import User
from django.db import models

class Executive(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    executive = models.ForeignKey(Executive, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    employee_secret_hash = models.CharField(max_length=255)
    employer_secret_hash = models.CharField(max_length=255)
    company_size = models.IntegerField()
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    skills = models.ManyToManyField(Skill, through="EmployeeSkill")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("employee", "skill")


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, through="RoleSkill")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class RoleSkill(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ("role", "skill")

class Education(models.Model):
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.school} - {self.degree} - {self.field_of_study}"
        
class RoleEducation(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    education = models.ForeignKey(Education, on_delete=models.CASCADE)

    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ("role", "education")


class EmployeeEducation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    education = models.ForeignKey(Education, on_delete=models.CASCADE)