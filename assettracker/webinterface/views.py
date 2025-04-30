from django.http import HttpResponse
from django.shortcuts import render
from .models import Asset

def index(request):
    assets = Asset.objects.filter(is_active=True).order_by('name')

    context = {
        'assets': assets,
    }

    return render(request, 'webinterface/asset_list.html', context)

def asset(request, asset_id):
    response = "You're looking at an asset %s."
    return HttpResponse(response % asset_id)
