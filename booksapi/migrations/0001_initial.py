# Generated by Django 4.1.4 on 2022-12-25 15:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('date_time_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('book_location', models.CharField(max_length=50)),
                ('isfav', models.BooleanField(default=False)),
                ('book_color', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=250)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]