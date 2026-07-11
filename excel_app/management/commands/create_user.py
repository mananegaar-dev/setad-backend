from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a user with username/password"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username")
        parser.add_argument("password", type=str, help="Password")
        parser.add_argument("--staff", action="store_true", help="Create as staff user")
        parser.add_argument("--superuser", action="store_true", help="Create as superuser")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"].strip()
        password = options["password"]
        is_staff = options["staff"] or options["superuser"]
        is_superuser = options["superuser"]

        if not username:
            raise CommandError("Username cannot be empty.")

        if User.objects.filter(username=username).exists():
            raise CommandError(f"User '{username}' already exists.")

        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

        role = "superuser" if is_superuser else ("staff" if is_staff else "user")
        self.stdout.write(self.style.SUCCESS(f"Created {role}: {user.username}"))
