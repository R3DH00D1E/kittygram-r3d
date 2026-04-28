from django.contrib.auth import get_user_model
from django.db import models

CHOICES = (
    ('Gray', 'Серый'),
    ('Black', 'Чёрный'),
    ('White', 'Белый'),
    ('Ginger', 'Рыжий'),
    ('Mixed', 'Смешанный'),
    ('Tabby', 'Полосатый'),
    ('Calico', 'Трёхцветный'),
    ('Cream', 'Кремовый'),
    ('Blue', 'Голубой'),
    ('Fawn', 'Палевый'),
)

User = get_user_model()


class Achievement(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16, choices=CHOICES)
    birth_year = models.IntegerField()
    owner = models.ForeignKey(
        User, related_name='cats', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cats/', null=True, blank=True)
    ownership_status = models.ForeignKey(
        'OwnershipStatus', null=True, blank=True, on_delete=models.SET_NULL, related_name='cats')
    achievements = models.ManyToManyField(Achievement, through='AchievementCat')

    def __str__(self):
        return self.name


class AchievementCat(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.achievement} {self.cat}'


class OwnershipStatus(models.Model):
    """Статусы владения котом (например: 'Владеет', 'В приюте', 'В поиске')."""
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name
