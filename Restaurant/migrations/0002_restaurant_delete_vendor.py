# Generated by Django 4.2.5 on 2023-10-14 04:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Restaurant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Restaurant_name', models.CharField(max_length=50)),
                ('Restaurant_license', models.ImageField(upload_to='Restaurant/license')),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to='accounts.userprofile')),
            ],
        ),
        migrations.DeleteModel(
            name='Vendor',
        ),
    ]
