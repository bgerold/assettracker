from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator

# Update default Django user model to add user phone number
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\s?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',
        message="Phone number must be entered in the format: '+1 (999) 999-9999'. Up to 15 digits allowed."
    )

    # Apply the validator to the phone_number field
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Trackable asset model
class Asset(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField(null=True, blank=True)
  home_location = models.CharField(max_length=255)
  purchase_date = models.DateField(null=True, blank=True)
  purchaser = models.CharField(max_length=100, null=True, blank=True)
  is_active = models.BooleanField(default=True)

  @property
  def current_checkout(self):
      return self.checkouts.filter(checkin_time__isnull=True).order_by('-checkout_time').first()

  @property
  def is_overdue(self):
      active_checkout = self.current_checkout 
      if active_checkout and active_checkout.expected_return_date:
          return active_checkout.expected_return_date < timezone.now().date()
      return False

  def __str__(self):
    return self.name

# Model for login check-outs & check-ins
class Checkout(models.Model):
  user = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.PROTECT,
      related_name='checkouts'
  )

  asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='checkouts')
  checkout_time = models.DateTimeField(default=timezone.now)
  expected_return_date = models.DateField()
  checkout_reason = models.TextField(null=True, blank=True)
  checkin_time = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    user_display = self.user.get_full_name() or self.user.username
    status = "Checked Out" if self.checkin_time is None else "Checked In"
    return f"{self.asset.name} by {user_display} ({status})"

  @property
  def is_overdue(self):
    if self.checkin_time is None and self.expected_return_date < timezone.now().date():
        return True
    return False
