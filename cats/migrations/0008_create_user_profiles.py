from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('cats', 'UserProfile')
    
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)


def delete_profiles(apps, schema_editor):
    UserProfile = apps.get_model('cats', 'UserProfile')
    UserProfile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cats', '0007_auto_20260503_1917'),
    ]

    operations = [
        migrations.RunPython(create_profiles, delete_profiles),
    ]
