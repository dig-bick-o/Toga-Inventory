from django.contrib import admin
from django.urls import path
from system import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('', views.admin_login, name='login'),  
    path('login/', views.admin_login, name='login'),
    path('signup/', views.signup_admin, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Password Recovery
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Admin Tools
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_student, name='add_student'),
    path('manage_admins/', views.manage_admins, name='manage_admins'),
    path('return/<int:student_id>/', views.mark_as_returned, name='mark_as_returned'),
    path('student/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('student/return/<int:id>/', views.mark_as_returned, name='mark_as_returned'),


]
