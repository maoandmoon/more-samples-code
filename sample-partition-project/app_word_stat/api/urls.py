from rest_framework import routers
from .views import CreateTaskViewSet, GetTaskInfoViewSet

APP_URL_API = 'word_stat'

router = routers.DefaultRouter()
router.register(r'{}/create_task'.format(APP_URL_API), CreateTaskViewSet,  base_name='create_task')
router.register(r'{}/status_task'.format(APP_URL_API), GetTaskInfoViewSet,  base_name='status_task')
