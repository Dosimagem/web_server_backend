from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from users.forms import SignUpForm


def index(request):
    return render(request, 'users/index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            user.refresh_from_db()
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.institution = form.cleaned_data.get('institution')
            user.profile.role = form.cleaned_data.get('role')
            user.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})


@login_required
def auth_example(request):
    return HttpResponse("You are autorized")
