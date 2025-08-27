from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme

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

                next_url = (
                    request.POST.get('next') or
                    request.GET.get('next') or
                    request.session.pop('next_url', None)
                )

                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                    return redirect(next_url)

                return redirect('home')
    else:
        form = CustomAuthenticationForm()
        if 'next' in request.GET:
            request.session['next_url'] = request.GET['next']

    return render(request, 'auth_app/login.html', {
        'form': form,
        'next': request.GET.get('next', '')  # Передаем next параметр в шаблон
    })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')

