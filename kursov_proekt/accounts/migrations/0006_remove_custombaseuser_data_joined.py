# Generated by Django 4.2 on 2024-12-16 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_custombaseuser_data_joined'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='custombaseuser',
            name='data_joined',
        ),
    ]