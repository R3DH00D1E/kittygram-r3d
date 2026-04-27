from django.db import migrations


ACHIEVEMENT_NAMES = [
    'Поймал лазер',
    'Спит 20 часов в сутки',
    'Король подоконника',
    'Лучший охотник на тапки',
    'Мурчит как трактор',
    'Чемпион по прыжкам',
    'Победитель в гляделках',
    'Самый пушистый хвост',
    'Покоритель коробок',
    'Хранитель дивана',
    'Лучший будильник в 5 утра',
    'Съел корм за 3 секунды',
    'Профи по тыгыдыку',
    'Знаток человеческой еды',
    'Мастер милых глаз',
]


def seed_achievements(apps, schema_editor):
    Achievement = apps.get_model('cats', 'Achievement')
    for name in ACHIEVEMENT_NAMES:
        Achievement.objects.get_or_create(name=name)


def unseed_achievements(apps, schema_editor):
    Achievement = apps.get_model('cats', 'Achievement')
    Achievement.objects.filter(name__in=ACHIEVEMENT_NAMES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cats', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_achievements, unseed_achievements),
    ]
