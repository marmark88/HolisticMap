from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('executive/', views.executive_dashboard, name='executive_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employer/', views.employer_dashboard, name='employer_dashboard'),

    path('create-company/', views.create_company, name='create_company'),
    path('delete-company/<int:company_id>/', views.delete_company, name='delete_company'),
    path('add-skill/', views.add_skill, name='add_skill'),
    path('remove-skill/<int:skill_id>/', views.remove_skill, name='remove_skill'),
    path('create-role/<int:company_id>/', views.create_role, name='create_role'),
    path('delete-role/<int:role_id>/', views.delete_role, name='delete_role'),
    path('role/<int:role_id>/', views.role_detail, name='role_detail'),
]