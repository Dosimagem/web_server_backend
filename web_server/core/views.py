from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from web_server.core.forms import SignupForm


def index(request):
    return render(request, 'core/index.html')


def signup(request):
    if request.method == 'POST':

        form_user = SignupForm(data=request.POST)

        if form_user.is_valid():

            user = form_user.save()
            # user.profile.name = form_user.cleaned_data['name']
            # user.profile.institution = form_user.cleaned_data['institution']
            # user.profile.role = form_user.cleaned_data['role']
            # user.profile.phone = form_user.cleaned_data['phone']
            # user.save()

            email = form_user.cleaned_data.get('email')
            raw_password = form_user.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)

            return redirect('core:login')
    else:
        form_user = SignupForm()

    context = {'form': form_user}

    return render(request, 'registration/signup.html', context=context)
