import os

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.utils import timezone

from tool_navigator.ToolNavigator.decorator import old_def_ajax
from work_project.settings import BASE_DIR, DEBUG
from app_programmatic.models import ModelProgrammaticFormatted, ModelSetting, LIST_STATUS, LIST_STATUS_CLASS
from tool_navigator.ToolNavigator import decorator_is_app_pex
from app_programmatic.forms import SettingForm
from celery_task.worker_programmatic.programmatic_worker import main as programmatic_worker

GLOBAL_APP_NAME = 'app_programmatic'
G_SLEEP_DAY = 1


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def index(request):
    disable_button = False
    all_programmatic = ModelProgrammaticFormatted.objects.all()
    if all_programmatic.exists():
        date_old = all_programmatic.order_by('date_time').reverse()[0].date_time.timestamp()
        data_time_update = timezone.now().timestamp() - date_old
        disable_button = data_time_update < G_SLEEP_DAY * (60 * 24)
        if DEBUG:
            disable_button = False
    return render(request, 'app_programmatic/index.html',
                  context={'is_page': 'main', 'sleep_day': G_SLEEP_DAY, 'disable_button': disable_button})


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def get_file(request, file_id):
    file_info = ModelProgrammaticFormatted.objects.filter(id=file_id)
    if file_info.exists():
        file_info = file_info.get()

        try:
            file_name = str(file_info.file_path.url).split('/')[-1]
            file_path = BASE_DIR + file_info.file_path.url

        except ValueError:
            return JsonResponse({
                "err": True,
                "text": "Ошибка, такого файла нет."
            })

        if os.path.isfile(file_path):

            with open(file_path, "rb") as excel:
                data = excel.read()

            response = HttpResponse(data,
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)

            return response
        else:
            # TODO Добавить обработку ошибок
            return JsonResponse({
                "err": True,
                "text": "Ошибка, такого файла нет."
            })

    # TODO Добавить обработку ошибок
    return JsonResponse({
        "err": True,
        "text": "Ошибка, такой записи нет."
    })


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def api_get_all_file(request):
    if request.method == "POST":
        all_programmatic = ModelProgrammaticFormatted.objects.all()
        if all_programmatic.exists():

            programmatic_list = [item for item in all_programmatic.order_by('date_time').reverse()]
            data_list = [{'id': i, 'status': item.id, 'file_path': [
                (lambda x: {'type': 'button', 'data': {
                    'text': _('Download'),
                    'url': str(reverse_lazy('app_programmatic:get_file', kwargs={'file_id': item.id}))}
                            } if x == 1 else {'type': 'span', 'data': {
                    'text': [i[1] for i in LIST_STATUS if i[0] == item.status],
                    'add_class': LIST_STATUS_CLASS[item.status],
                }})(
                    item.status)],
                          'date_time': str(item.date_time.__format__("%Y-%m-%d")),
                          'date_time_old': str(
                              "{}".format(item.date_time.month - 1, ))}
                         for item, i in zip(programmatic_list, range(len(programmatic_list) + 1)[1:])]

            return JsonResponse({
                'err': False,
                'data': {
                    "table_name_list": [_('#'), _("Data create"), _('Month of report'), _('file')],
                    "table_ids_list": ['id', 'date_time', 'date_time_old', 'file_path'],
                    "items_list": data_list
                }
            })
        else:
            return JsonResponse({
                'err': True,
                'text': ''
            })
    else:
        return JsonResponse({
            'err': True,
            'text': None
        })


@require_POST
@old_def_ajax
@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def refresh_stat(request):
    all_programmatic = ModelProgrammaticFormatted.objects.all()
    if all_programmatic.exists():
        date_old = all_programmatic.order_by('date_time').reverse()[0].date_time.timestamp()
        data_time_update = timezone.now().timestamp() - date_old

        if data_time_update < G_SLEEP_DAY * (60 * 24):
            return {
                'err': False,
                'text': _('Заявка уже была обновленна ') + str(data_time_update / 60) + _(' день/дней назад.'),
                'alert_color': "warning",
            }

    date_time_now = timezone.now()
    item_program_form = ModelProgrammaticFormatted(date_time=date_time_now, status=0)

    item_program_form.save()
    if DEBUG:
        programmatic_worker(item_program_form.id)
    else:
        programmatic_worker.delay(item_program_form.id)

    return {
        'err': False,
        'text': 'Формирование отчета успешно запущено',
        'alert_color': "success",
    }


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def setting_default(users, new_status=None):
    user_setting = ModelSetting.objects.filter(is_user_id=users)
    if user_setting.exists():

        if new_status is not None:
            user_setting.update(notification_status=new_status)
            notification_status = new_status
        else:
            notification_status = user_setting.get().notification_status

    else:
        user_setting = ModelSetting(is_user_id=users, notification_status=False)
        user_setting.save()
        notification_status = False
    return notification_status


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def setting(request):
    notification_status = setting_default(request.user)

    error_text = None
    error_url_text = None
    if request.method == "POST":
        form = SettingForm(request.POST)
        if form.is_valid():
            push_notification = form.cleaned_data['push_notification']
            notification_status = setting_default(request.user, push_notification)
        else:
            error_text = _('Error, not all fields are full or format error.')
    else:
        form = SettingForm(request.POST)

        notification_status = setting_default(request.user)

    if request.user.email == '' and notification_status:
        error_text = _('Attention! You must create an email address!')
        error_url_text = _('Setting')

    return render(request, 'app_programmatic/setting.html',
                  context={'form': form, 'notif_status': notification_status,
                           'is_page': "setting", 'error': (lambda x: x if x is not None else None)(error_text),
                           'error_url_text': error_url_text})
