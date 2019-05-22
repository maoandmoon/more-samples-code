from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

# Create your models here.

LIST_STATUS = (
    (0, _('Waiting for a queue')),
    (1, _('Done')),
    (2, _('Error on script')),
    (3, _('Error on server'))
)

LIST_STATUS_CLASS = ({
    0: "badge-primary",
    1: "badge-success",
    2: "badge-danger",
    3: "badge-danger",
})


class ModelProgrammaticFormatted(models.Model):
    file_path = models.FileField(upload_to='app_programmatic/files/', default=None, null=True, blank=True,
                                 max_length=500)
    date_time = models.DateTimeField()
    status = models.IntegerField(choices=LIST_STATUS)


class ModelSetting(models.Model):
    is_user_id = models.ForeignKey(User)
    notification_status = models.BooleanField()
