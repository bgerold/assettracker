from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Subquery, Value, IntegerField
from django.db.models.functions import Coalesce
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from .models import Asset, Checkout
from django.db import transaction

def index(request):
    # Subquery to find the ID of the active checkout for an asset
    active_checkout_id_subquery = Checkout.objects.filter(
        asset=OuterRef('pk'),
        checkin_time__isnull=True
    ).values('pk')[:1]

    # Subquery to check if an active checkout exists (for boolean flag)
    active_checkout_exists_subquery = Checkout.objects.filter(
        asset=OuterRef('pk'),
        checkin_time__isnull=True
    )

    # Get the asset list, filtering for active assets
    assets = Asset.objects.filter(is_active=True).annotate(
        is_checked_out=Exists(active_checkout_exists_subquery),
        active_checkout_id=Coalesce(Subquery(active_checkout_id_subquery), Value(None, output_field=IntegerField()))
    ).order_by('name') # Order results


    # Get a list of resent check-ins / checkout-outs
    recent_checkouts = Checkout.objects.order_by('-checkout_time')[:10]

    context = {
        'assets': assets,
        'recent_checkouts': recent_checkouts,
    }

    return render(request, 'webinterface/asset_list.html', context)

@login_required # Ensure user is logged in
def checkout_asset_view(request, asset_id):
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('webinterface:index')

    try:
        with transaction.atomic():
            asset_to_checkout = get_object_or_404(Asset, pk=asset_id, is_active=True)
            is_already_checked_out = Checkout.objects.filter(
                asset=asset_to_checkout,
                checkin_time__isnull=True
            ).exists()

            if is_already_checked_out:
                messages.error(request, f"'{asset_to_checkout.name}' is already checked out.")
                return redirect('webinterface:index')
            default_return_date = timezone.now().date() + timedelta(days=7)
            new_checkout = Checkout.objects.create(
                asset=asset_to_checkout,
                user=request.user,
                checkout_time=timezone.now(),
                expected_return_date=default_return_date,
            )
            messages.success(request, f"Successfully checked out '{asset_to_checkout.name}'. Please return by {default_return_date.strftime('%Y-%m-%d')}.")

    except Exception as e:
        messages.error(request, f"An error occurred during checkout: {e}")

    return redirect('webinterface:index')

# HTTP Post to updated asset to a status of "checked in"
@login_required # Ensure user is logged in
def checkin_asset_view(request, checkout_id):
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('webinterface:index')

    try:

        checkout_record = get_object_or_404(Checkout, pk=checkout_id, checkin_time__isnull=True)

        # Update the checkin_time
        checkout_record.checkin_time = timezone.now()
        checkout_record.save()
        messages.success(request, f"Successfully checked in '{checkout_record.asset.name}'.")

    except Checkout.DoesNotExist:
        messages.error(request, "This checkout record was not found or has already been checked in.")
    except Exception as e:
        messages.error(request, f"An error occurred during check-in: {e}")

    return redirect('webinterface:index') # Use namespaced index
