# Common functions (Used in multiple views or management functions)
from django.conf import settings
from django.contrib.auth.models import User
from webinterface.models import UserProfile
from .models import Asset
from .models import Checkout
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

# Create a logger instance
logger = logging.getLogger(__name__)

def send_email(username, content):
    logger.info("Sending asset overdue email to %s" % username)

    api_key = settings.SENDGRID_API_KEY

    try:
        user_object = User.objects.get(username=username)
    except:
        logger.error("User %s does not exist" % username)
        return "Invalid User Name"

    message = Mail(
                from_email = 'bryan.gerold@my.trident.edu',
                to_emails = user_object.email,
                subject = 'Overdue Asset',
                plain_text_content = content)
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
    
    except Exception as e:
        print(e)
        return "Failed to send notification"
    
    return "Success"

def send_sms(username, content):
    logger.info("Send asset overdue sms to %s" % username)

    try:
        user_object = User.objects.get(username=username)
    except:
        logger.error("User %s does not exist" % username)
        return "Invalid Username"
    
    try:
        to_phone_number = "+1" + user_object.profile.phone_number
    except:
        logger.error("User profile does not exist")
        return "User profile does not exist"

    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_phone_number = settings.TWILIO_FROM_NUMBER
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=content,
            from_=from_phone_number,
            to=to_phone_number,
        )
    
    except:
        logger.error("Failed to send message to Twilio API")
        return "Failed to send message to Twilio API"

    return "Success"

def send_overdue_asset_notifications():
    logger.info("Check for overdue assets")

    notifications_sent_count = 0
    notifications_failed_count = 0
    overdue_checkouts_found_count = 0

    # Iterate through these and then check their `is_overdue` property.
    active_checkouts = Checkout.objects.filter(
        checkin_time__isnull=True
    ).select_related('user__profile', 'asset')

    if not active_checkouts.exists():
        logger.info("No active checkouts found requiring overdue check.")
        return {"found_overdue": 0, "sent": 0, "failed": 0}

    logger.info(f"Checking {active_checkouts.count()} active checkouts for overdue status.")

    for checkout in active_checkouts:
         # We rely on the 'is_overdue' property of the Checkout model.
         if hasattr(checkout, 'is_overdue') and checkout.is_overdue:
            overdue_checkouts_found_count += 1
            
            user = checkout.user
            asset = checkout.asset # Asset is now directly available from the checkout object
            email_sent = False
            sms_sent = False

            # Prepare notification messages using details from the checkout record
            message = (
                f"Dear {user.get_full_name() or user.username},\n\n"
                f"This is a reminder that the asset '{asset.name}' (Description: {asset.description or 'N/A'}) "
                f"which you checked out on {checkout.checkout_time.strftime('%Y-%m-%d %H:%M')} "
                f"was due for return on {checkout.expected_return_date.strftime('%Y-%m-%d')}.\n\n"
                f"Please return it to its home location: {asset.home_location} as soon as possible.\n\n"
                f"Thank you,\nAsset Tracking System"
            )

            if send_email(user.username, message) ==  "Success":
                notifications_sent_count += 1
            else:
                notifications_failed_count +=1

            if send_sms(user.username, message) ==  "Success":
                notifications_sent_count += 1
            else:
                notifications_failed_count +=1

    summary = {
        "found_overdue": overdue_checkouts_found_count, # Number of checkouts whose is_overdue property was true
        "sent": notifications_sent_count,
        "failed": notifications_failed_count
    }
    
    logger.info(f"Overdue notification process completed. Summary: {summary}")
    
    return summary