from django.contrib import admin

from app_programmatic.models import ModelProgrammaticFormatted


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'status')
    list_filter = ('date_time', 'status')


admin.site.register(ModelProgrammaticFormatted, AuthorAdmin)
