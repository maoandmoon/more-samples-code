import re

from django.utils import timezone
from rest_framework.response import Response
from rest_framework import viewsets
from app_word_stat.api.serializers import CreateTask
from app_word_stat.forms import AddTaskWordStat, GetTaskInfo
from app_word_stat.models import ModelTask, ModelWordList
from app_word_stat.tasks import get_word_stat
from work_project.settings import DEBUG


class GetTaskInfoViewSet(viewsets.ViewSet):
    """
    Doc: [Get task info](https://bitbucket.org/ErmakovV/publicistoolnavigator/wiki/GetTaskInfo)

    """

    def list(self, request):

        form = GetTaskInfo(request.query_params)
        if form.is_valid():
            if form.cleaned_data['task_id'].user_id == request.user:
                return Response({
                    "data": {
                        "status": form.cleaned_data['task_id'].status,
                        "url": "http://dtitools.ru/static/app_word_stat/tmp/task_id_{}.csv".format(form.cleaned_data['task_id'].id)
                    },
                    "code": 2000,
                })
            else:
                return Response({
                    "data": {
                        "err_text": "not_permission",
                        "err_trace": form.errors,
                    },
                    "code": 4503,
                }, status=403)
        else:
            return Response({
                "data": {
                    "err_text": "is_not_valid",
                    "err_trace": form.errors,
                },
                "code": 4500,
            }, status=400)


class CreateTaskViewSet(viewsets.ViewSet):
    """
    Doc: [Create Task](https://bitbucket.org/ErmakovV/publicistoolnavigator/wiki/CreateTaskViewSet)
    """

    serializer_class = CreateTask

    def create(self, request):
        form = AddTaskWordStat(request.POST)
        if form.is_valid():

            words_list = [re.sub(r'\s+', ' ', str(s)) for s in re.split(r"[\n\t]", str(form.cleaned_data['text']))]

            task = ModelTask(user_id=request.user, data_time=timezone.now(), regions_type=form.cleaned_data['region'],
                             db_type=form.cleaned_data['device'], period_type=form.cleaned_data['period'], status=1,
                             task_name='REST_API: {}'.format(words_list[0][:25]))
            task.save()

            for word in words_list:
                if word != "":
                    word_id = ModelWordList.objects.filter(word=word)
                    if word_id.exists():
                        word_id = word_id.get()
                    else:
                        word_id = ModelWordList(word=word)
                        word_id.save()
                    task.is_words.add(word_id.id)
            task.save()

            if not DEBUG:
                get_word_stat.delay(task.id)

            return Response({
                "data": {
                    "task_id": task.id,
                },
                "code": 2000,
            })
        else:
            return Response({
                "data": {
                    "err_text": "is_not_valid",
                    "err_trace": form.errors,
                },
                "code": 4500,
            }, status=400)
