# Generated by Django 4.2 on 2024-12-19 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_alter_billingdetails_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingdetails',
            name='account_password',
        ),
    ]