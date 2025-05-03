from django.contrib import admin
from django.urls import include, path
from webinterface import views as webinterface_views

urlpatterns = [
    # Direct the root URL to the web interface's index page
    path('', webinterface_views.index, name='home'),

    # URL route for the 'webinterface' Django Application
    path("webinterface/", include("webinterface.urls")),

    # URL route for the builtin admin applicaiton
    path('admin/', admin.site.urls),
]

