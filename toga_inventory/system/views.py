from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
import random

from .forms import StudentForm
from .models import Student

# Utility: Superuser check
def is_superuser(user):
    return user.is_superuser

# Admin Signup (Pending approval)
def signup_admin(request):
    if request.method == 'POST':
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken.'})

        if User.objects.filter(email=email, is_staff=True).exists():
            return render(request, 'signup.html', {'error': 'Email already registered. Try logging in.'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_active = False
        user.save()

        return render(request, 'signup.html', {'message': 'Account submitted for approval.'})
        
    return render(request, 'signup.html')

# Superuser View: Manage Admins
@user_passes_test(is_superuser)
@staff_member_required
def manage_admins(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = int(request.POST.get('user_id'))
        user = User.objects.get(id=user_id)

        if action == 'approve':
            user.is_active = True
            user.save()
            messages.success(request, f"{user.username} approved as admin.")

        elif action == 'reject':
            user.delete()
            messages.warning(request, f"{user.username} has been rejected and removed.")

        elif action == 'delete':
            if request.user.id == user.id:
                messages.error(request, "You cannot delete your own account while logged in.")
            else:
                user.delete()
                messages.success(request, f"{user.username} has been deleted.")

        return redirect('manage_admins')

    # Load admin lists
    all_admins = User.objects.filter(is_staff=True, is_active=True)
    pending_admins = User.objects.filter(is_staff=True, is_active=False)

    return render(request, 'manage_admins.html', {
        'all_admins': all_admins,
        'pending_admins': pending_admins,
    })

# Admin Login
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active and user.is_staff:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials or account not approved.'})

    return render(request, 'login.html')

# Forgot Password
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp

            send_mail(
                'Your Password Reset OTP',
                f'Your OTP is: {otp}',
                'noir062003@gmail.com',  # Change to real sender
                [email],
                fail_silently=False,
            )
            return redirect('verify_reset_otp')
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Email not found.'})

    return render(request, 'forgot_password.html')

# Verify OTP
def verify_reset_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('reset_otp'):
            return redirect('reset_password')
        else:
            return render(request, 'verify_reset_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'verify_reset_otp.html')

# Reset Password
def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match.'})

        email = request.session.get('reset_email')
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            request.session.flush()
            return redirect('login')
        except User.DoesNotExist:
            return redirect('forgot_password')

    return render(request, 'reset_password.html')

# Dashboard View
#@login_required
def dashboard(request):
    user = request.user
    if user.is_active and user.is_staff:
        students = Student.objects.all().order_by('-borrowed_date')
        return render(request, 'dashboard.html', {'students': students})
    return render(request, 'not_approved.html')

# Add Student
@login_required
def add_student(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.status = 'Borrowed'
        student.save()
        return redirect('dashboard')
    return render(request, 'add_student.html', {'form': form})

# Logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Mark Student as Returned
@login_required
def mark_as_returned(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == 'POST' and not student.returned_date:
        student.returned_date = timezone.now()
        student.status = 'Returned'
        student.save()
    return redirect('dashboard')


# Delete Student
@login_required
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    if request.method == 'POST':
        student.delete()
    return redirect('dashboard')
