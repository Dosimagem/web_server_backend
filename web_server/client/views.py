from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from web_server.client.orders import Orders


@login_required
def profile(request):
    orders = Orders(request.user)
    return render(request, 'profile/profile.html', context={'solicitations': orders.all_orders()})
