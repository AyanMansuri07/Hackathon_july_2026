from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import CustomUser
import random

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'AssetFlowApp/register.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'AssetFlowApp/register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'AssetFlowApp/register.html')

        otp = str(random.randint(100000, 999999))
        print('=' * 32)
        print(f'Generated OTP : {otp}')
        print('=' * 32)

        request.session['registration_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone_number': phone,
            'password': make_password(password)
        }
        request.session['otp'] = otp
        request.session['otp_time'] = str(timezone.now())

        return redirect('otp_verify')

    return render(request, 'AssetFlowApp/register.html')

def otp_verify_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        reg_data = request.session.get('registration_data')

        if not session_otp or not reg_data:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')

        if entered_otp != session_otp:
            messages.error(request, 'OTP is incorrect. Please try again.')
            return render(request, 'AssetFlowApp/otp.html')

        user = CustomUser.objects.create(
            email=reg_data['email'],
            first_name=reg_data['first_name'],
            last_name=reg_data['last_name'],
            phone_number=reg_data['phone_number'],
            password=reg_data['password']
        )
        
        del request.session['otp']
        del request.session['otp_time']
        del request.session['registration_data']

        messages.success(request, 'Registration successful. Please login.')
        return redirect('login')

    return render(request, 'AssetFlowApp/otp.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email not found.')
            return render(request, 'AssetFlowApp/login.html')

        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Wrong password.')
            return render(request, 'AssetFlowApp/login.html')

    return render(request, 'AssetFlowApp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def forgot_password_view(request):
    return render(request, 'AssetFlowApp/forgot_password.html')

def dashboard_view(request):
    return render(request, 'AssetFlowApp/dashboard.html')
