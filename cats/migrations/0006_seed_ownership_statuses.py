from django.db import migrations


OWNERSHIP_STATUS_DATA = [
    ('У владельца', 'Кот живет у владельца и находится под его постоянной опекой.'),
    ('На передержке', 'Кот временно живет у волонтера или в приюте.'),
    ('В поиске дома', 'Коту нужен новый дом и постоянный хозяин.'),
    ('Передан новому владельцу', 'Кот уже нашел нового хозяина.'),
    ('Нуждается в заботе', 'Коту требуется особое внимание и уход.'),
]


def seed_ownership_statuses(apps, schema_editor):
    OwnershipStatus = apps.get_model('cats', 'OwnershipStatus')
    for name, description in OWNERSHIP_STATUS_DATA:
        OwnershipStatus.objects.get_or_create(
            name=name,
            defaults={'description': description},
        )


def unseed_ownership_statuses(apps, schema_editor):
    OwnershipStatus = apps.get_model('cats', 'OwnershipStatus')
    OwnershipStatus.objects.filter(name__in=[name for name, _ in OWNERSHIP_STATUS_DATA]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cats', '0005_alter_cat_color'),
    ]

    operations = [
        migrations.RunPython(seed_ownership_statuses, unseed_ownership_statuses),
    ]
