from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            USR = settings.ADM_USR
            PSS = settings.ADM_PSS
        except AttributeError:
            USR = "admin"
            PSS = "admin"
        if not User.objects.filter(username=USR).exists():
            User.objects.create_superuser(USR, "admin@admin.com", PSS)