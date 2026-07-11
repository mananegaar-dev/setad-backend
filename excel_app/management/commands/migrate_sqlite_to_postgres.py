import os
import json

from django.conf import settings
from django.db import models
from django.core.management import BaseCommand, call_command, CommandError
from django.apps import apps


class Command(BaseCommand):
    help = "Migrate data from sqlite_legacy database to default (PostgreSQL)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default="/tmp/sqlite_legacy_dump.json",
            help="Temporary fixture path",
        )
        parser.add_argument(
            "--keep-fixture",
            action="store_true",
            help="Keep fixture file after import",
        )
        parser.add_argument(
            "--flush-target",
            action="store_true",
            help="Flush target database (default) before loading data",
        )

    @staticmethod
    def _sanitize_fixture_dates(fixture_path):
        with open(fixture_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        model_map = {m._meta.label_lower: m for m in apps.get_models()}
        fixed_count = 0

        for item in payload:
            model_label = item.get("model")
            model = model_map.get(model_label)
            if not model:
                continue

            fields = item.get("fields", {})
            for field in model._meta.concrete_fields:
                if field.name not in fields:
                    continue
                value = fields[field.name]
                if value in (None, ""):
                    continue
                if isinstance(field, (models.DateField, models.DateTimeField)):
                    try:
                        field.to_python(value)
                    except Exception:
                        fields[field.name] = None
                        fixed_count += 1

        with open(fixture_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        return fixed_count

    def handle(self, *args, **options):
        if "sqlite_legacy" not in settings.DATABASES:
            raise CommandError("sqlite_legacy database is not configured.")

        sqlite_path = str(settings.DATABASES["sqlite_legacy"]["NAME"])
        if not os.path.exists(sqlite_path):
            raise CommandError(f"sqlite legacy file not found: {sqlite_path}")

        fixture_path = options["fixture"]
        keep_fixture = options["keep_fixture"]
        flush_target = options["flush_target"]

        self.stdout.write("Dumping data from sqlite_legacy...")
        call_command(
            "dumpdata",
            database="sqlite_legacy",
            output=fixture_path,
            exclude=[
                "contenttypes",
                "auth.permission",
                "admin.logentry",
                "auth_app.useractivitylog",
            ],
            natural_foreign=True,
            natural_primary=True,
        )

        fixed_dates = self._sanitize_fixture_dates(fixture_path)
        if fixed_dates:
            self.stdout.write(f"Fixed invalid date/datetime values: {fixed_dates}")

        if flush_target:
            self.stdout.write("Flushing target database...")
            call_command("flush", database="default", interactive=False)

        self.stdout.write("Loading data into default database...")
        call_command(
            "loaddata",
            fixture_path,
            database="default",
            ignorenonexistent=True,
        )

        if not keep_fixture and os.path.exists(fixture_path):
            os.remove(fixture_path)

        self.stdout.write(self.style.SUCCESS("SQLite data migrated to PostgreSQL successfully."))
