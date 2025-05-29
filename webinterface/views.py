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
from django import forms

class CheckoutForm(forms.Form):
    expected_return_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        label="Expected Return Date"
    )
    checkout_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        label="Reason for Checkout (Optional)",
        required=False 
    )

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
    asset = get_object_or_404(Asset, pk=asset_id)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():

            Checkout.objects.create(
                asset=asset,
                user=request.user,
                checkout_time=timezone.now(),
                expected_return_date=form.cleaned_data['expected_return_date'],
                checkout_reason=form.cleaned_data['checkout_reason']
            )
            messages.success(request, f"Asset '{asset.name}' checked out successfully.")
            return redirect('webinterface:index')
        else:
            # Form is invalid, re-render the page with errors
            pass
    else:
        form = CheckoutForm()

    return render(request, 'webinterface/checkout_details.html', {
        'form': form,
        'asset': asset
    })

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
