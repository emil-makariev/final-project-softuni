# Generated by Django 5.1.3 on 2024-11-19 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_custombaseuser_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='custombaseuser',
            name='confirm_password',
            field=models.IntegerField(default=None),
        ),
    ]
