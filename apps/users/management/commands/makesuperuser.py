import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

User = get_user_model()

load_dotenv()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
        try:
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write("No superusers found, creating one.....")
                User.objects.create_superuser(email=email, password=password)
                self.stdout.write("A superuser has been created")
            else:
                self.stdout.write("A superuser exists in the database. Skipping.")
        except Exception as e:
            self.stderr.write(f"There was an error {e}")
