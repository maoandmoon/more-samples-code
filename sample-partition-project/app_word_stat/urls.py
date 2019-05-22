from django.conf.urls import url, include
from app_word_stat.views import index, add_task, task_result, api_get_all_word, api_get_task_info, api_task_refresh, \
    api_delete_task, api_get_all_task, double_task

# from django.conf.urls import url, include


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^add_task/$', add_task, name='add_task'),
    url(r'^task_result/(?P<task_id>\d+)/$', task_result, name='task_result'),
    url(r'^double_task/(?P<task_id>\d+)/$', double_task, name='double_task'),

    # Client (users) API
    url(r'^api/get_all_word/(?P<task_id>\d+)/$', api_get_all_word, name='api_get_all_word'),
    url(r'^api/get_task_info/(?P<task_id>\d+)/$', api_get_task_info, name='api_get_task_info'),
    url(r'^api/get_task_refresh/(?P<task_id>\d+)/$', api_task_refresh, name="api_get_task_refresh"),
    url(r'^api/delete_task/(?P<task_id>\d+)/$', api_delete_task, name='api_delete_task'),
    url(r'^api/get_all_task/$', api_get_all_task, name='api_get_all_task'),
]
