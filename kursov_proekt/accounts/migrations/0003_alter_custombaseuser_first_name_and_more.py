# Generated by Django 5.1.3 on 2024-11-18 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_custombaseuser_first_name_custombaseuser_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custombaseuser',
            name='first_name',
            field=models.CharField(),
        ),
        migrations.AlterField(
            model_name='custombaseuser',
            name='last_name',
            field=models.CharField(),
        ),
    ]
