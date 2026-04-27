from rest_framework import serializers

import datetime as dt

from .models import CHOICES, Achievement, Cat, User


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
        ref_name = 'ReadOnlyUsers'


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'name')


class CatSerializer(serializers.ModelSerializer):
    achievements = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Achievement.objects.all(),
        required=False
    )
    color = serializers.ChoiceField(choices=CHOICES)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'achievements', 'owner',
                  'age')

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        achievements = validated_data.pop('achievements', [])
        cat = Cat.objects.create(**validated_data)
        if achievements:
            cat.achievements.set(achievements)
        return cat

    def update(self, instance, validated_data):
        achievements = validated_data.pop('achievements', None)
        instance = super().update(instance, validated_data)
        if achievements is not None:
            instance.achievements.set(achievements)
        return instance
