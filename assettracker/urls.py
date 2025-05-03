from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # URL route for the 'webinterface' Django Application
    path("webinterface/", include("webinterface.urls")),

    # URL route for the builtin admin applicaiton
    path('admin/', admin.site.urls),
]

