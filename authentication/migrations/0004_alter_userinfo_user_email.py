# Generated by Django 4.2.2 on 2023-06-10 00:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_alter_userinfo_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='user_email',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
