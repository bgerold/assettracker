# Managment command that triggers overdue asset notification logic

from django.core.management.base import BaseCommand
from webinterface.utils import send_overdue_asset_notifications

class Command(BaseCommand):
    help = 'Run overdue asset notificaiton logic'

    def handle(self, *args, **options):

        send_overdue_asset_notifications()

