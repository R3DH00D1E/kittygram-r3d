from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cats', '0002_seed_achievements'),
    ]

    operations = [
        migrations.AddField(
            model_name='cat',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='cats/'),
        ),
    ]
