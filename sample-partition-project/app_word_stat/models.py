from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from solo.models import SingletonModel

# Create your models here.

PERIOD_TYPE_LIST = [None, 'weekly']
PERIOD_TYPE_LIST_LANG = [_('Month'), _('Week')]

DB_TYPE_LIST = [None, 'desktop', 'mobile', 'phone', 'tablet']
DB_TYPE_LIST_LANG = [_('All'), _('Desktops'), _('Mobile phones'), _('Only phones'), _('Tablets only')]

REGIONS_TYPES = (
    (0, "Все"),
    (225, 'Россия'),
    (1, 'Москва и область'),
    (213, 'Москва'),
    (10174, 'Санкт-Петербург и Ленинградская область'),
    (2, 'Санкт-Петербург'),
    (166, 'СНГ (исключая Россию)'),
    (111, 'Европа'),
    (183, 'Азия'),
    (3, 'Центр'),
    (17, 'Северо-Запад'),
    (40, 'Поволжье'),
    (26, 'Юг'),
    (59, 'Сибирь'),
    (73, 'Дальний Восток'),
    (977, 'Республика Крым'),
    (102444, 'Северный Кавказ'),
    (52, 'Урал')
)

TASK_STATUS = (
    (1, _('not processed')),
    (2, _('processing in progress')),
    (3, _('done')),
    (4, _('error')),
)

TASK_STATUS_CLASS = ({
    1: "badge-secondary",
    2: "badge-primary",
    3: "badge-success",
    4: "badge-danger",
})


def get_type_is_id(int_code, list_name, list_human_name=None):
    """
    Преобразуем 2'ый код в лист

    :param int_code:  2'ый код
    :param list_name: лист с уникальным именем категории
    :param list_human_name: лист с именами для пользователя
    :return: лист с 2 именами: уникальным и для пользователя
    """
    name_list = []
    for stats, period, name in zip(reversed(bin(int_code)[2:]), list_name, list_human_name):
        if bool(int(stats)):
            name_list.append([period, name])

    return name_list


class ModelWordList(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word


class ModelTask(models.Model):
    task_name = models.CharField(max_length=65)
    user_id = models.ForeignKey(User)
    data_time = models.DateTimeField()
    is_words = models.ManyToManyField(to=ModelWordList)
    regions_type = models.IntegerField(null=True, blank=True)  # Тип региона
    db_type = models.IntegerField()  # Тип устройств
    period_type = models.IntegerField()  # Тип периуда

    # Поле со статусов (скорее всего будет 2 статуса, 1 - Все ок, 2 - Файл удален)
    status = models.IntegerField(default=1, choices=TASK_STATUS)

    def get_regions_type(self):
        if self.regions_type is not None:
            return self.regions_type


class ModelWordsFile(models.Model):
    task_id = models.OneToOneField(to=ModelTask)
    file_name = models.FileField(upload_to='public/app_word_stat/tmp/csv/')  # Путь до файла
    date = models.DateField()  # Дата создания файла


class ModelYandexUsers(models.Model):
    user_id = models.ForeignKey(User)
    users = models.ManyToOneRel('username', User, user_id)
    y_login = models.CharField(max_length=255, null=True)
    y_password = models.CharField(max_length=255, null=True)
    cookies = models.CharField(max_length=255)
    count = models.IntegerField()
    status = models.IntegerField()


class ModelAppConf(SingletonModel):
    api_key = models.CharField(max_length=50)
    def_login = models.CharField(max_length=50)
    def_password = models.CharField(max_length=50)
    def_cookies = models.TextField(max_length=3000, null=True, blank=True)
    region_json = models.TextField(max_length=1000000, null=True, blank=True)
