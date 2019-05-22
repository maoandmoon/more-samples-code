# -*- coding: utf-8 -*-
# TODO: !!! Рефакторинг кода и вынести все в отдельный class
# TODO: Слишком много булирования кода, очень большие функции
import time

import re
from django.db.models.functions import datetime
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone, formats
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from tool_navigator.ToolNavigator import *
from tool_navigator.ToolNavigator.decorator import old_def_ajax
from tool_navigator.models import ModelAppInfo
from work_project.settings import DEBUG
from .models import ModelTask, ModelWordList, REGIONS_TYPES, TASK_STATUS, TASK_STATUS_CLASS
from .tasks import get_word_stat

GLOBAL_APP_NAME = 'app_word_stat_yandex'

period_type_list = [None, 'weekly']
period_type_list_lang = [_('Month'), _('Week')]

db_type_list = [None, 'desktop', 'mobile', 'phone', 'tablet']
db_type_list_lang = [_('All'), _('Desktops'), _('Mobile phones'), _('Only phones'), _('Tablets only')]


def get_type_is_id(int_code: int, list_name):
    name_list = []

    for stats, period in zip(reversed(bin(int_code)[2:]), list_name):
        if bool(int(stats)):
            name_list.append(period)
    return name_list


def get_app_info():
    app_info = ModelAppInfo.objects.get(unique_app_name=GLOBAL_APP_NAME)
    return app_info


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def index(request):
    return render(request, template_name='app_word_stat/index.html', context={
        "app_info": get_app_info(),
        "is_page": "word_stat"
    })


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def add_task(request):
    if request.method == 'POST':

        item = dict(request.POST)
        if 'textarea' in item and 'period' in item and 'db' in item and \
           item['textarea'][0] != "" and 'reg_name' in item:

            users_words_list = [re.sub(r'\s+', ' ', str(s)) for s in re.split(r"[\n\t]", str(item['textarea'][0]))]

            if 'task_name' in item and item['task_name'][0] != '':
                task_name = re.sub(r'\s+', ' ', str(item['task_name'][0]))
                if task_name == ' ':
                    task_name = ", ".join(users_words_list[:3])
            else:
                task_name = ", ".join(users_words_list[:3])

            try:
                user_period = int(item['period'][0])
                user_db = int(item['db'][0])
                user_reg = int(item['reg_name'][0])
            except ValueError:
                return JsonResponse({
                    'err': True,
                    'text': 'Ошибка POST запроса. Попытка отправить строку.'
                })

            task = ModelTask(user_id=request.user, data_time=timezone.now(), regions_type=user_reg, db_type=user_db,
                             period_type=user_period, status=1, task_name=task_name)
            task.save()

            for word in users_words_list:
                if word != "":
                    word_id = ModelWordList.objects.filter(word=word)
                    if word_id.exists():
                        word_id = word_id.get()
                    else:
                        word_id = ModelWordList(word=word)
                        word_id.save()
                    task.is_words.add(word_id.id)
            task.save()

            get_word_stat.delay(task.id)

            return JsonResponse({
                "err": False,
                "id": task.id,
                "url": reverse_lazy('app_word_stat:task_result', kwargs={'task_id': task.id})
            })

        else:
            return JsonResponse({
                'err': True,
                'text': "Не все поля заполенн."
            })
    else:
        return render(request, template_name='app_word_stat/add_task.html', context={
            "regions_list": REGIONS_TYPES,
            "is_page": "add_task"
        })


def get_bit_str(int_str):
    return str(bin(int_str))[2:][::-1]


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def double_task(request, task_id):
    user_id = request.user.id

    if request.user.is_superuser:
        get_info = ModelTask.objects.filter(id=task_id)
    else:
        get_info = ModelTask.objects.filter(id=task_id, user_id=user_id)

    if get_info.extra():
        get_info = get_info.get()

        return render(request, template_name='app_word_stat/add_task.html', context={
            "task_id": get_info.id,
            "task_name": get_info.task_name,
            "task_date": get_info.data_time,
            "edit_task": True,
            "regions_list": REGIONS_TYPES,
            "is_page": "add_task",
            "edit_task_name": get_info.task_name,
            "edit_words_list": get_info.is_words.all(),
            "edit_db_type": get_bit_str(get_info.db_type),
            "edit_period_type":  get_bit_str(get_info.period_type),
            "edit_regions_type": get_info.regions_type,
        })
    else:
        return HttpResponseRedirect(reverse_lazy('app_word_stat:index'))


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def task_result(request, task_id):
    user_id = request.user.id

    # Маленькая возможность для супер пользователя
    if request.user.is_superuser:
        get_info = ModelTask.objects.filter(id=task_id)
    else:
        get_info = ModelTask.objects.filter(id=task_id, user_id=user_id)

    if get_info.exists():
        get_info = get_info.get()

        if get_info.is_words.exists():

            reg_type = None
            for reg in REGIONS_TYPES:
                if reg[0] == get_info.regions_type:
                    reg_type = reg[1]

            db_list = ", ".join(get_type_is_id(get_info.db_type, db_type_list_lang)).lower()
            period_list = ", ".join(get_type_is_id(get_info.period_type, period_type_list_lang)).lower()

            return render(request, template_name='app_word_stat/task_result.html', context={
                "reg_type": reg_type,
                "task_info": get_info,
                "db_list": db_list,
                "period_list": period_list,
                "status": get_info.status,
                "error": False
            })

    return render(request, template_name='app_word_stat/task_result.html', context={
        "error": True,
        "id_task": task_id,
        "err_text": "Такого ID нет в списке ваших заявок."
    })


@require_POST
@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def api_get_all_word(request, task_id):
    # Маленькая возможность для супер пользователя
    if request.user.is_superuser:
        task_info = ModelTask.objects.filter(id=task_id)
    else:
        task_info = ModelTask.objects.filter(id=task_id, user_id=request.user.id)

    if task_info.exists():
        task_info = task_info.get()

        return JsonResponse({
            "err": False,
            "word_list": [s.word for s in
                          ModelTask.objects.get(id=task_id, user_id=task_info.user_id.id).is_words.all()]
        })
    else:
        return JsonResponse({
            "err": True,
            "text": "Ошибка 403: у вас нет прав. (Обратитесь к разработчику)"
        })


@require_POST
@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def api_get_task_info(request, task_id):
    # Маленькая возможность для супер пользователя
    if request.user.is_superuser:
        task_info = ModelTask.objects.filter(id=task_id)
    else:
        task_info = ModelTask.objects.filter(id=task_id, user_id=request.user.id)

    if task_info.exists():
        task_info = task_info.get()

        reg_type = None
        for reg in REGIONS_TYPES:
            if reg[0] == task_info.regions_type:
                reg_type = reg[1]

        secondary = ['secondary', 'primary', 'success', 'danger']

        task_status = None
        for i, color in zip(TASK_STATUS, secondary):
            if task_info.status == i[0]:
                task_status = {'id': i[0], 'name': i[1], 'color': color}

        return JsonResponse({
            "err": False,
            "data": {
                "date": task_info.data_time.__format__("%Y-%m-%d"),
                "reg": reg_type,
                "type": ", ".join(get_type_is_id(task_info.db_type, db_type_list_lang)).lower(),
                "period": ", ".join(get_type_is_id(task_info.period_type, period_type_list_lang)).lower(),
                "user": task_info.user_id.username,
                "status": task_status,
            }
        })
    else:
        return JsonResponse({
            "err": True,
            "text": "Ошибка 403: у вас нет прав. (Обратитесь к разработчику)"
        })


@require_POST
@old_def_ajax
@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def api_task_refresh(request, task_id):
    # Маленькая возможность для супер пользователя
    if request.user.is_superuser:
        task_info = ModelTask.objects.filter(id=task_id)
    else:
        task_info = ModelTask.objects.filter(id=task_id, user_id=request.user.id)

    if task_info.exists():
        task_info = task_info.get()
        min_int = 20
        if not (task_info.status in [3, 4]) \
                and task_info.data_time.timestamp() + min_int * 60 > datetime.datetime.now().timestamp():
            return {'err': True,
                    'info': _('Task is processing, refresh will be available in {} minutes.'.format(min_int))}

        task_info.status = 1
        task_info.data_time = timezone.now()
        task_info.save()

        if not DEBUG:
            get_word_stat.delay(task_id)

        return {'err': False,
                'info': _(
                    'task: {}, start updating task.'.format(task_info.task_name))
                }
    else:
        return {
            "err": True,
            "text": "Error trying to retry task, id {}.".format(task_id)
        }


@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def api_delete_task(request, task_id):
    # Маленькая возможность для супер пользователя
    if request.user.is_superuser:
        task_info = ModelTask.objects.filter(id=task_id)
    else:
        task_info = ModelTask.objects.filter(id=task_id, user_id=request.user.id)

    if task_info.exists():
        task_info.delete()
        return HttpResponseRedirect(reverse_lazy('app_word_stat:index'))
    else:
        return render(request, template_name='app_word_stat/index.html', context={
            "app_info": get_app_info(),
            "is_page": "word_stat",
        })


@require_POST
@old_def_ajax
@decorator_is_app_pex(app_name=GLOBAL_APP_NAME)
def api_get_all_task(request):
    task_info = ModelTask.objects.filter(user_id=request.user.id)
    if task_info.exists():
        task_list_not_clean = [i for i in
                               ModelTask.objects.filter(user_id=request.user.id).order_by('data_time').reverse()]
        task_list = [{
            "id": i, "task_name": [{"type": "url",
                                    "data": {
                                        "text": item.task_name,
                                        "url":
                                            str(reverse_lazy('app_word_stat:task_result', kwargs={'task_id': item.id}))
                                    }}],
            "date_time": formats.date_format(item.data_time),
            "button": [
                {"type": "button", "data": {
                    "text": _("Edit/Double"),
                    "url": str(reverse_lazy('app_word_stat:double_task', kwargs={'task_id': item.id})),
                }},
                {"type": "button", "data": {
                    "text": _("Download"),
                    "add_class": (lambda x: "" if x == 3 else "disabled")(item.status),
                    "url": "/static/app_word_stat/tmp/task_id_{}.csv".format(item.id),
                }},
                {"type": "button", "data": {
                    "text": _("Delete"),
                    "add_class": 'btn-outline-danger',
                    "url": str(reverse_lazy('app_word_stat:api_delete_task', kwargs={'task_id': item.id})),
                }},
                {'type': 'button', 'data': {
                    'text': (lambda x, y: _('Refresh {} min'.format(time.strftime("%M", time.gmtime(x + 60))))
                             if x > 0 and not (y in [3, 4])else _('Refresh'))(
                        (item.data_time.timestamp() + 20 * 60 - datetime.datetime.now().timestamp()), item.status),
                    'url': str(reverse_lazy('app_word_stat:api_get_task_refresh', kwargs={'task_id': item.id})),
                    'disabled': (lambda x, y: True if not (x in [3, 4])
                                 and y + 20 * 60 > datetime.datetime.now().timestamp()
                                 else False)(item.status, item.data_time.timestamp()),
                    'use_js': True,
                }},
            ],
            "status": [{"type": "span", "data": {
                "text": [i for i in TASK_STATUS if i[0] == item.status][0][1],
                "add_class": TASK_STATUS_CLASS[item.status]
            }}]
        } for item, i in zip(task_list_not_clean, range(len(task_list_not_clean) + 1)[1:])]

        return {
            'err': False,
            'data': {
                "table_name_list": [_('#'), _("task name"), _("date"), '', _('status')],
                "table_ids_list": ['id', 'task_name', 'date_time', 'button', 'status'],
                "items_list": task_list
            }}
