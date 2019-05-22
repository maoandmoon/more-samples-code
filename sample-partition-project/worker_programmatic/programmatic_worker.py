# coding : utf-8
from django.utils import timezone
from django.core.files import File

from app_programmatic.models import ModelProgrammaticFormatted
from work_project.celery import app


@app.task
def main(item_programmatic_id):
    file_path = None

    for i in range(10):
        try:
            file_path = '/file/path/'
            break
        except Exception as err:
            is_item = ModelProgrammaticFormatted.objects.filter(id=item_programmatic_id)
            is_item.update(status=2)

            raise err

    if file_path is None:
        return 'Error', 'file path is None'

    is_item = ModelProgrammaticFormatted.objects.get(id=item_programmatic_id)

    is_item.file_path.save('file.xlsx', File(open(file_path, 'rb')))
    is_item.status = 1
    is_item.save()

    #  Отправка email:
    # for user_info in ModelSetting.objects.filter(notification_status=True):
    #    if user_info.is_user_id.email != '':
    #        send_db_mail('programmatic_new_report', user_info.is_user_id.email, {
    #            "date": str(date_time_now.__format__("%Y-%m-%d")),
    #            "file_id": item_programmatic_id,
    #            "url_download": ALLOWED_HOSTS[0] + str(
    #                reverse_lazy('app_programmatic:get_file', kwargs={'file_id': item_programmatic_id})),
    #            "url_stop_spam": ALLOWED_HOSTS[0] + str(reverse_lazy('app_programmatic:setting'))
    #        })


if __name__ == '__main__':
    item_program_form = ModelProgrammaticFormatted(date_time=timezone.now(), status=0)

    item_program_form.save()
    main(item_program_form.id)
