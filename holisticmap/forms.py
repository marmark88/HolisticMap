from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Company

class ExecutiveRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'phone')

# Employer Registration
class EmployerRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=255)
    company = forms.ModelChoiceField(queryset=Company.objects.all())
    company_secret = forms.CharField(max_length=255, help_text="Enter your employer password")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'name', 'phone', 'company', 'company_secret']

# Employee Registration
class EmployeeRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=255)
    company = forms.ModelChoiceField(queryset=Company.objects.all())
    company_secret = forms.CharField(max_length=255, help_text="Enter your employee password")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'name', 'phone', 'company', 'company_secret']