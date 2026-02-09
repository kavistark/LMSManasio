from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AdminUser

# 🔐 Fixed Superuser Login
def superuser_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'admin' and password == 'admin123':
            request.session['superuser_logged_in'] = True
            return redirect('superuser_dashboard')
        else:
            messages.error(request, 'Invalid Superuser Credentials')

    return render(request, 'superuser_admin/login_page.html')


# 🏠 Dashboard
def superuser_dashboard(request):
    if not request.session.get('superuser_logged_in'):
        return redirect('superuser_login')

    return render(request, 'superuser_admin/dashboard.html')


# ➕ Add Admin
def add_admin(request):
    if not request.session.get('superuser_logged_in'):
        return redirect('superuser_login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if AdminUser.objects.filter(username=username).exists():
            messages.error(request, 'Admin already exists')
        else:
            AdminUser.objects.create(username=username, password=password)
            messages.success(request, 'Admin created successfully')
            return redirect('admin_manage')

    return render(request, 'superuser_admin/add_admin.html')


# 📋 Manage Admins
def admin_manage(request):
    if not request.session.get('superuser_logged_in'):
        return redirect('superuser_login')

    admins = AdminUser.objects.all()
    return render(request, 'superuser_admin/admin_manage.html', {'admins': admins})


# 🚪 Logout
def superuser_logout(request):
    request.session.flush()
    return redirect('superuser_login')
