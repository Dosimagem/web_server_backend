from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from web_server.client.orders import Orders


@login_required
def profile(request):
    orders = Orders(request.user)
    return render(request, 'client/profile.html', context={'solicitations': orders.all_orders()})


@login_required
def dosimetry_order(request):
    return render(request, 'client/dosimetry_order.html')
