from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from web_server.users.forms import SignUpForm


class Solicitation:

    def __init__(self, user, status, type_service, report_link, request_data):
        self.user = user
        self.status = status
        self.type_service = type_service
        self.report_link = report_link
        self.request_data = request_data


SOLICITATIONS = [Solicitation('Henrique', 'Processando', 'Dosimetria Clinica', 'link', '10/10/2022'),
                 Solicitation('Henrique', 'Concluído', 'Dosimetria Pré-clinica', 'link', '06/10/2022')]


def index(request):
    return render(request, 'users/index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():

            user = form.save()

            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)

            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html', context={'solicitations': SOLICITATIONS})
