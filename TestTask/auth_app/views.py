from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth_app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                next_url = request.POST.get('next') or request.session.pop('next_url', None)
                if next_url:
                    return redirect(next_url)
                return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = CustomAuthenticationForm()

    next_param = request.GET.get('next') or request.session.get('next_url')
    return render(request, 'auth_app/login.html', {
        'form': form,
        'next': next_param
    })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')

