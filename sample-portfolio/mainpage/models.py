from django.db import models
from django.core.validators import FileExtensionValidator
from datetime import datetime


class PersonalInfo(models.Model):
    name = models.CharField(max_length=255)
    expert_at = models.CharField(max_length=255)
    image = models.ImageField(upload_to='image/%Y/%m/%d', max_length=255)
    about = models.TextField(max_length=1024)
    contact = models.CharField(max_length=17)
    email = models.EmailField(max_length=255)
    address = models.CharField(max_length=255)
    fb_link = models.CharField(max_length=255)
    linkedin_link = models.CharField(max_length=255)
    insta_link = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Skill(models.Model):
    title = models.CharField(max_length=52, unique=True)
    description = models.TextField(max_length=1024)
    icon = models.FileField(upload_to='icon/%Y/%m/%d',
                            validators=[FileExtensionValidator(['svg'])])

    def __str__(self):
        return self.title


class Partner(models.Model):
    title = models.CharField(max_length=52, unique=True)
    icon = models.ImageField(upload_to='partners/%Y/%m/%d')

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=52, unique=True)
    description = models.TextField(max_length=1024)
    snapshot_1 = models.ImageField(upload_to='project/%Y/%m/%d')
    snapshot_2 = models.ImageField(upload_to='project/%Y/%m/%d', blank=True)
    snapshot_3 = models.ImageField(upload_to='project/%Y/%m/%d', blank=True)
    project_type = models.ManyToManyField(Skill)
    started = models.DateField()
    ended = models.DateField()

    def __str__(self):
        return self.title


class Message(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    body = models.TextField(max_length=1024)
    reply = models.TextField(max_length=1024, blank=True, null=True)
    sent = models.DateTimeField(default=datetime.now)
    is_replied = models.BooleanField(default=False)

    def __str__(name):
        return self.title
