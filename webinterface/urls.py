from django.urls import path
from . import views

app_name = 'webinterface'

urlpatterns = [
    path("", views.index, name="index"),

    # Path for checkout action
    path("checkout/<int:asset_id>/", views.checkout_asset_view, name="checkout_asset"),

    # Path for Checkin
    path("checkin/<int:checkout_id>/", views.checkin_asset_view, name="checkin_asset"),
]