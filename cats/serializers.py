from rest_framework import serializers

import datetime as dt

from .models import CHOICES, Achievement, Cat, User, OwnershipStatus


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'cats')
        ref_name = 'ReadOnlyUsers'


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'name')


class OwnershipStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnershipStatus
        fields = ('id', 'name', 'description')


class CatSerializer(serializers.ModelSerializer):
    achievements = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Achievement.objects.all(),
        required=False
    )
    image = serializers.ImageField(required=False, allow_null=True)
    ownership_status = serializers.PrimaryKeyRelatedField(queryset=OwnershipStatus.objects.all(), required=False, allow_null=True)
    color = serializers.ChoiceField(choices=CHOICES)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'achievements', 'owner',
                  'ownership_status', 'image', 'age')
        read_only_fields = ('owner',)

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
