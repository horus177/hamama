from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

# صفحة تسجيل حساب جديد
def register_view(request):
    if request.user.is_authenticated:
        return redirect('farm_home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'تم إنشاء الحساب وتسجيل الدخول بنجاح! 🥳')
            return redirect('farm_home')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# صفحة تسجيل الدخول
def login_view(request):
    if request.user.is_authenticated:
        return redirect('farm_home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'أهلاً بك مجدداً يا {user.username} 👋')
            return redirect('farm_home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# تسجيل الخروج
def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('login')