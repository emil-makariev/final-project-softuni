# Generated by Django 5.1.3 on 2024-11-19 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_custombaseuser_confirm_password'),
    ]

    operations = [
        migrations.RenameField(
            model_name='custombaseuser',
            old_name='confirm_password',
            new_name='password2',
        ),
    ]
