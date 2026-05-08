from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Ownership status'
        verbose_name_plural = 'Ownership statuses'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    consent_personal = models.BooleanField(default=False)
    consent_personal_date = models.DateTimeField(null=True, blank=True)
    consent_photo = models.BooleanField(default=False)
    consent_photo_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Profile for {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'profile') and instance.profile:
            instance.profile.save()
    except Exception:
        pass
