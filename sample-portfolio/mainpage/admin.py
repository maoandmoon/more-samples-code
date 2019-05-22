from django import forms
from django.contrib import admin
from .models import *
# Register your models here.


class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'expert_at', 'email', 'contact',)
    list_display_links = ('name',)


class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'description',)
    list_display_links = ('title',)
    search_fields = ('title',)
    list_per_page = 20


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)
    list_display_links = ('title',)
    search_fields = ('title',)
    list_per_page = 20


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'started', 'ended', )
    list_display_links = ('title',)
    filter_horizontal = ('project_type',)
    search_fields = ('title',)
    list_per_page = 20


class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_replied', 'sent',)
    list_display_links = ('name',)
    search_fields = ('name', 'email',)
    list_filter = ('is_replied',)
    list_per_page = 20


admin.site.register(PersonalInfo, PersonalInfoAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Message, MessageAdmin)
