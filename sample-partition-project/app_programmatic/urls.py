from django.conf.urls import url
from .views import index, api_get_all_file, get_file, setting, refresh_stat

urlpatterns = [
    url(r'^$', index, name='main'),
    url(r'^get_file/(?P<file_id>\d+)/$', get_file, name='get_file'),
    url(r'^setting/$', setting, name='setting'),
    url(r'^refresh_stat/$', refresh_stat, name='refresh_stat'),

    url(r'^api/get_all_file/$', api_get_all_file, name='api_get_all_file')
]
