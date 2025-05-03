from django.core.management.base import BaseCommand
from webinterface.utils import send_email

class Command(BaseCommand):
    help = 'Send a test email to the specified user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to send test email to')
        parser.add_argument('assetid', type=int, help="Asset ID value for overdue asset")

    def handle(self, *args, **options):
        username = options['username']
        assetid = options['assetid']
        
        send_email(username, assetid)

