from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from app_word_stat.models import REGIONS_TYPES, ModelTask
from app_word_stat.views import period_type_list, db_type_list


def period_validate(value):
    if not(type(value) is int and 0 < len(bin(value)[2:]) <= len(period_type_list)):
        raise ValidationError(_('%(value)s is not (0 < len(bin(value)) <= len(period_type_list))'), params={'value': value}, )


def device_validate(value):
    if not(type(value) is int and 0 < len(bin(value)[2:]) <= len(db_type_list)):
        raise ValidationError(_('%(value)s is not (type(value) is int and 0 < len(bin(value)) <= len(db_type_list))'),
                              params={'value': value}, )


def region_validate(value):
    if not(value in dict(REGIONS_TYPES)):
        raise ValidationError(_('%(value), нет такого региона в списке.'), params={'value': value}, )


class AddTaskWordStat(forms.Form):
    text = forms.CharField()
    period = forms.IntegerField(validators=[period_validate])
    device = forms.IntegerField(validators=[device_validate])
    region = forms.IntegerField(validators=[region_validate])


class GetTaskInfo(forms.Form):
    task_id = forms.ModelChoiceField(queryset=ModelTask.objects.filter())
