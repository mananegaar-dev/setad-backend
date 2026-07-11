from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "اضافه کردن کاربر به نقش (Group) مشخص"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='نام کاربری کاربر')
        parser.add_argument('role', type=str, help='نام نقش (Group name)')

    def handle(self, *args, **options):
        username = options['username']
        role_name = options['role']

        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"کاربری با نام '{username}' پیدا نشد.")

        group, created = Group.objects.get_or_create(name=role_name)

        user.groups.add(group)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"نقش '{role_name}' ساخته شد و به کاربر '{username}' اضافه گردید."))
        else:
            self.stdout.write(self.style.SUCCESS(f"کاربر '{username}' به نقش '{role_name}' اضافه شد."))
