from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'

class LogoutView(auth_views.LogoutView):
    next_page = '/'

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
