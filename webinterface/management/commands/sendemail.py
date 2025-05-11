# Managment command parser for sending test email notificaitons to a specified user

from django.core.management.base import BaseCommand
from webinterface.utils import send_email

class Command(BaseCommand):
    help = 'Send a test email to the specified user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to send test email to')

    def handle(self, *args, **options):
        username = options['username']
        
        send_email(username, "Test Message")

