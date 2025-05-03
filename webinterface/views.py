from django.http import HttpResponse
from django.shortcuts import render
from .models import Asset, Checkout

def index(request):
    # Get the asset list
    assets = Asset.objects.filter(is_active=True).order_by('name')

    # Get a list of checked out assets. TODO: Right now just showing all assets....
    recent_checkouts = Checkout.objects.order_by('-checkout_time')[:10]

    context = {
        'assets': assets,
        'recent_checkouts': recent_checkouts,
    }

    return render(request, 'webinterface/asset_list.html', context)
