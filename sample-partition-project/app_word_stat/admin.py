from django.contrib import admin
from solo.admin import SingletonModelAdmin

from django.utils import timezone
from django.utils.translation import ugettext as _

from work_project.settings import DEBUG
from .models import ModelTask, ModelWordList, ModelWordsFile, ModelYandexUsers, ModelAppConf


def restart_task(modeladmin, request, queryset):
    if not DEBUG:
        from .tasks import get_word_stat
        for i in queryset:
            get_word_stat.delay(i.id)
    queryset.update(status=1, data_time=timezone.now())
    short_description = _("Restart task")


class AuthorAdmin(admin.ModelAdmin):
    pass


class TaskAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'task_name', 'data_time', 'regions_type', 'db_type', 'period_type', 'status')
    list_filter = ('data_time', 'regions_type', 'db_type', 'period_type', 'status')
    actions = [restart_task]


admin.site.register(ModelTask, TaskAdmin)
admin.site.register(ModelWordList, AuthorAdmin)
admin.site.register(ModelWordsFile, AuthorAdmin)
admin.site.register(ModelYandexUsers, AuthorAdmin)

admin.site.register(ModelAppConf, SingletonModelAdmin)
