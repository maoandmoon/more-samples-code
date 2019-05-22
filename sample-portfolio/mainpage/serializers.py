from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from . import models


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'expert_at', 'image', 'about', 'contact', 'email',
                  'address', 'fb_link', 'linkedin_link', 'insta_link',)
        model = models.PersonalInfo


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title', 'icon', 'description',)
        model = models.Skill


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title', 'icon',)
        model = models.Partner


class ProjectSerializer(serializers.ModelSerializer):
    project_type = SkillSerializer(many=True, read_only=True)

    class Meta:
        fields = ('title', 'project_type', 'snapshot_1', 'snapshot_2',
                  'snapshot_3', 'started', 'ended', 'description',)
        model = models.Project


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'email', 'body',)
        model = models.Message

    def validate_email(self, value):
        try:
            message = models.Message.objects.get(email=value)
            if message.is_replied:
                return value
            raise serializers.ValidationError(
                'please wait before previous message is replied')
        except ObjectDoesNotExist:
            return value
