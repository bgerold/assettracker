# Common functions (Used in multiple views or management functions)
from django.conf import settings
from django.contrib.auth.models import User
from webinterface.models import UserProfile
from .models import Asset
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Create a logger instance
logger = logging.getLogger(__name__)

def send_email(username, assetid):
    logger.info("Sending asset overdue email to %s" % username)

    api_key = settings.SENDGRID_API_KEY

    try:
        user_object = User.objects.get(username=username)
    except:
        logger.error("User %s does not exist" % username)
        return "Invalid User Name"
    
    try:
        asset_object = Asset.objects.get(id=assetid)
    except:
        logger.error("Asset %s does not exist" % assetid)
        return "Invalid Asset ID"
    
    print(asset_object.name)

    content = f"Asset {asset_object.name} ({asset_object.description}) is more than 24 hours overdue"

    message = Mail(
                from_email = 'bryan.gerold@my.trident.edu',
                to_emails = user_object.email,
                subject = 'Overdue Asset',
                plain_text_content = content)
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    
    except Exception as e:
        print(e)
        return "Failed to send notification"
    
    return "Success"

def send_sms(username, assetid):
    logger.info("Send asset overdue sms to %s" % username)

    try:
        user_object = User.objects.get(username=username)
    except:
        logger.error("User %s does not exist" % username)
        return "Invalid Username"
    
    try:
        asset_object = Asset.objects.get(id=assetid)
    except:
        logger.error("Asset %s does not exist" % assetid)
        return "Invalid Asset ID"
    
    print(user_object.profile.phone_number)

    return "Success"
