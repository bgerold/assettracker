from django.contrib import admin
from .models import Asset, Checkout
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from webinterface.utils import send_email
from webinterface.utils import send_sms

# Make the Asset and Checkout models editable in the bultin admin console
admin.site.register(Asset)
admin.site.register(Checkout)

# Define an inline admin page the user profile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define a new User admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)
    
    def response_change(self, request, obj):
        username = obj.username

        if "test_sms" in request.POST:
            result = send_sms(username, 1)
            self.message_user(request, f"Sending test notification to {username} complted with status {result}")
            return HttpResponseRedirect(".")
        
        if "test_email" in request.POST:
            result = send_email(username, 1)
            self.message_user(request, f"Sending test notification to {username} complted with status {result}")
            return HttpResponseRedirect(".")


        return super().response_change(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
