from django.db import migrations

def populate_default_categories(apps, schema_editor):
    Category = apps.get_model('product', 'Category')  # Adjust the app label if necessary
    # Add categories if they don't already exist
    Category.objects.get_or_create(name='Clothes')
    Category.objects.get_or_create(name='Shoes')
    Category.objects.get_or_create(name='Accessories')

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),  # Adjust this to match the last migration
    ]

    operations = [
        migrations.RunPython(populate_default_categories),
    ]
