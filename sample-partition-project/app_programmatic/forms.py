from django import forms
from django.utils.translation import ugettext as _


class SettingForm(forms.Form):
    push_notification = forms.BooleanField(label=_("Отправлять уведомления на электронную почту"), required=False, initial=False)
