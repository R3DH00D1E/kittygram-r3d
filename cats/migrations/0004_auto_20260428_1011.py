from django.db import migrations, models
import django.db.models.deletion
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cats', '0003_cat_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='OwnershipStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('description', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.AddField(
            model_name='cat',
            name='ownership_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cats', to='cats.ownershipstatus'),
        ),
    ]
