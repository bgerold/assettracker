from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("webinterface/", include("webinterface.urls")),
    path('admin/', admin.site.urls),
]
