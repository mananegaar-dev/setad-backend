# Generated manually for Otp model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6)),
                ('otp_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_now', models.DateTimeField(auto_now_add=True)),
                ('expire', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
