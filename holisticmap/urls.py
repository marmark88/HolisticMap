from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register-executive/', views.register_executive, name='register_executive'),
    path('register-employer/', views.register_employer, name='register_employer'),
    path('register-employee/', views.register_employee, name='register_employee'),

    path('executive/', views.executive_dashboard, name='executive_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employer/', views.employer_dashboard, name='employer_dashboard'),

    path('create-company/', views.create_company, name='create_company'),
    path('delete-company/<int:company_id>/', views.delete_company, name='delete_company'),
    path('add-skill/', views.add_skill, name='add_skill'),
    path('remove-skill/<int:skill_id>/', views.remove_skill, name='remove_skill'),
    path('add-education/', views.add_education, name='add_education'),
    path('remove-education/<int:education_id>/', views.remove_education, name='remove_education'),
    path('create-role/<int:company_id>/', views.create_role, name='create_role'),
    path('delete-role/<int:role_id>/', views.delete_role, name='delete_role'),
    path('role/<int:role_id>/', views.role_detail, name='role_detail'),
    path(
        'role/<int:role_id>/employee/<int:employee_id>/',
        views.role_employee_match_detail,
        name='role_employee_match_detail',
    ),
]