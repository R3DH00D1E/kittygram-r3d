from django.db import migrations
from django.contrib.auth.hashers import make_password


def seed_user_and_cats(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Cat = apps.get_model('cats', 'Cat')
    Achievement = apps.get_model('cats', 'Achievement')
    AchievementCat = apps.get_model('cats', 'AchievementCat')
    OwnershipStatus = apps.get_model('cats', 'OwnershipStatus')

    if not User.objects.filter(username='user').exists():
        user = User.objects.create(
            username='user',
            email='user@example.com',
            first_name='Test',
            last_name='User',
            password=make_password('user')
        )
    else:
        user = User.objects.get(username='user')

    cats_data = [
        {
            'name': 'Мурзик',
            'color': 'Ginger',
            'birth_year': 2020,
            'status': 'У владельца',
            'achievements': ['Поймал лазер', 'Чемпион по прыжкам', 'Мурчит как трактор'],
        },
        {
            'name': 'Васька',
            'color': 'Black',
            'birth_year': 2021,
            'status': 'На передержке',
            'achievements': ['Король подоконника', 'Самый пушистый хвост', 'Лучший будильник в 5 утра'],
        },
        {
            'name': 'Снежок',
            'color': 'White',
            'birth_year': 2022,
            'status': 'В поиске дома',
            'achievements': ['Покоритель коробок', 'Хранитель дивана', 'Мастер милых глаз'],
        },
    ]

    for cat_data in cats_data:

        ownership_status = OwnershipStatus.objects.filter(name=cat_data['status']).first()

        cat, created = Cat.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'color': cat_data['color'],
                'birth_year': cat_data['birth_year'],
                'owner': user,
                'ownership_status': ownership_status,
            }
        )

        if not created and cat.ownership_status != ownership_status:
            cat.ownership_status = ownership_status
            cat.save()

        for achievement_name in cat_data['achievements']:
            achievement = Achievement.objects.filter(name=achievement_name).first()
            if achievement:
                AchievementCat.objects.get_or_create(
                    achievement=achievement,
                    cat=cat,
                )


def unseed_user_and_cats(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='user').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cats', '0008_create_user_profiles'),
    ]

    operations = [
        migrations.RunPython(seed_user_and_cats, unseed_user_and_cats),
    ]
