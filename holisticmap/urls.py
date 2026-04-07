from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('executive/', views.executive_dashboard, name='executive_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),

    path('create-company/', views.create_company, name='create_company'),
    path('add-skill/', views.add_skill, name='add_skill'),
]