import json

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy

from app_word_stat.models import ModelTask
from work_project.settings import URL_LOGIN
from app_word_stat.views import GLOBAL_APP_NAME


class WordStatTests(TestCase):
    def setUp(self):
        group_item = Group.objects.get(name=GLOBAL_APP_NAME)

        User.objects.create_user('user', 'temporary@gmail.com', 'temporary')
        user_item = User.objects.create_user('user_is_group', 'temporary@gmail.com', 'temporary')
        user_item.groups.add(group_item)

        user_item_1 = User.objects.create_user('user_is_group_1', 'temporary@gmail.com', 'temporary')
        user_item_1.groups.add(group_item)

    def test_index_url(self):
        response = self.client.get(reverse_lazy('app_word_stat:index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:index')))

        self.client.login(username='user_is_group', password='temporary')
        response = self.client.get(reverse_lazy('app_word_stat:index'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user', password='temporary')
        response = self.client.get(reverse_lazy('app_word_stat:index'))
        self.assertEqual(response.status_code, 403)
        # self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:index')))

    def test_add_task_url(self):
        response = self.client.get(reverse_lazy('app_word_stat:add_task'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:add_task')))

        self.client.login(username='user_is_group', password='temporary')
        response = self.client.get(reverse_lazy('app_word_stat:add_task'))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user', password='temporary')
        response = self.client.get(reverse_lazy('app_word_stat:add_task'))
        self.assertEqual(response.status_code, 403)
        # self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:add_task')))

    def test_add_task(self):
        self.client.login(username='user', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:add_task'),
                                    {'textarea': 'test\nis test1\nis test2\tis test 5', 'period': '1', 'db': '1',
                                     'reg_name': '1'})
        self.assertEqual(response.status_code, 403)
        # self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:add_task')))

        self.client.login(username='user_is_group', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:add_task'),
                                    {'textarea': 'test\nis test1\nis test2\tis test 5', 'period': '1', 'db': '1',
                                     'reg_name': '1'})
        response_json = json.loads(response.content.decode())

        self.assertFalse(response_json['err'])
        self.assertEqual(response_json['id'], 1)
        self.assertEqual(response_json['url'], reverse_lazy('app_word_stat:task_result', kwargs={'task_id': 1}))

        response = self.client.post(reverse_lazy('app_word_stat:add_task'),
                                    {'textarea': '', 'period': '1', 'db': '1', 'reg_name': '1'})
        response_json = json.loads(response.content.decode())

        self.assertTrue(response_json['err'])
        self.assertEqual(type(response_json['text']), str)

        response = self.client.post(reverse_lazy('app_word_stat:add_task'),
                                    {'textarea': '', 'period': 'фыв123123', 'db': '1', 'reg_name': '1'})
        response_json = json.loads(response.content.decode())

        self.assertTrue(response_json['err'])
        self.assertEqual(type(response_json['text']), str)

        response = self.client.post(reverse_lazy('app_word_stat:add_task'),
                                    {'textarea': '', 'period': 'фыв123123', 'db': '123фыв123', 'reg_name':
                                        'фыв12312фыв123'})
        response_json = json.loads(response.content.decode())

        self.assertTrue(response_json['err'])
        self.assertEqual(type(response_json['text']), str)

        response = self.client.post(reverse_lazy('app_word_stat:add_task'),
                                    {'textarea': 'фыв123', 'period': '123123', 'db': '1312', 'reg_name': '11112ы'})
        response_json = json.loads(response.content.decode())

        self.assertTrue(response_json['err'])
        self.assertEqual(type(response_json['text']), str)

    def test_task_result_url(self):
        response = self.client.get(reverse_lazy('app_word_stat:task_result', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:task_result',
                                                                                   kwargs={'task_id': 1})))

        self.client.login(username='user_is_group', password='temporary')
        response = self.client.get(reverse_lazy('app_word_stat:task_result', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user', password='temporary')
        response = self.client.get(reverse_lazy('app_word_stat:task_result', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 403)
        # self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:task_result',
        #                                                                            kwargs={'task_id': 1})))

    def test_get_all_word(self):
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_word', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:api_get_all_word',
                                                                                   kwargs={'task_id': 1})))

        self.client.login(username='user_is_group', password='temporary')
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                                    {'textarea': 'test\nis test1\nis test2\tis test 5', 'period': '1', 'db': '1',
                                     'reg_name': '1'})

        self.client.logout()
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_word', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:api_get_all_word',
                                                                                   kwargs={'task_id': 1})))

        self.client.login(username='user', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_word', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 403)
        # self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:api_get_all_word',
        #                                                                            kwargs={'task_id': 1})))

        self.client.login(username='user_is_group', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_word', kwargs={'task_id': 1}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_json = json.loads(response.content.decode())

        self.assertFalse(response_json['err'])
        self.assertEqual(response_json, {'err': False, 'word_list': ['test', 'is test1', 'is test2', 'is test 5']})

        self.client.login(username='user_is_group_1', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_word', kwargs={'task_id': 1}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_json = json.loads(response.content.decode())

        self.assertTrue(response_json['err'])
        self.assertEqual(type(response_json['text']), str)

    def test_get_task_info(self):
        response = self.client.post(reverse_lazy('app_word_stat:api_get_task_info', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:api_get_task_info',
                                                                                   kwargs={'task_id': 1})))

        self.client.login(username='user_is_group', password='temporary')
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                         {'textarea': 'test\nis test1\nis test2\tis test 5', 'period': '1', 'db': '1',
                          'reg_name': '1'})

        self.client.logout()
        response = self.client.post(reverse_lazy('app_word_stat:api_get_task_info', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:api_get_task_info',
                                                                                   kwargs={'task_id': 1})))

        self.client.login(username='user', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_task_info', kwargs={'task_id': 1}))
        self.assertEqual(response.status_code, 403)
        # self.assertEqual(response.url, '{}?next={}'.format(URL_LOGIN, reverse_lazy('app_word_stat:api_get_task_info',
        #                                                                            kwargs={'task_id': 1})))

        self.client.login(username='user_is_group', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_task_info', kwargs={'task_id': 1}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_json = json.loads(response.content.decode())

        user_get = User.objects.get(username='user_is_group')
        task_info = ModelTask.objects.get(id=1, user_id=user_get)

        self.assertFalse(response_json['err'])
        self.assertEqual(response_json, {'err': False,
                                         'data': {'date': task_info.data_time.__format__("%Y-%m-%d"),
                                                  'user': 'user_is_group', 'status':
                                                      {'id': 1, 'name': 'not processed', 'color': 'secondary'},
                                                  'reg': 'Москва и область', 'type': 'все', 'period': 'month'
                                                  }})

        self.client.login(username='user_is_group_1', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_task_info', kwargs={'task_id': 1}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_json = json.loads(response.content.decode())

        self.assertTrue(response_json['err'])
        self.assertEqual(type(response_json['text']), str)

    def test_tesk_refrash(self):
        pass

    def test_delete_task(self):
        pass

    def test_get_all_task(self):
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_task'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_json = json.loads(response.content.decode())
        self.assertEqual(response_json['content'], '{}?next={}'.format(URL_LOGIN,
                                                                       reverse_lazy('app_word_stat:api_get_all_task')))

        self.client.login(username='user', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_task'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_json = json.loads(response.content.decode())
        # self.assertEqual(response_json['content'], '{}?next={}'.format(URL_LOGIN,
        #                                                                reverse_lazy('app_word_stat:api_get_all_task')))

        self.client.login(username='user_is_group', password='temporary')
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                         {'textarea': 'sdas123asdtest\nis test1\nis test2\tis test 5123123', 'period': '3', 'db': '1',
                          'reg_name': '4'})
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                         {'textarea': 'sdas123asdtest\nis test1\nis test2\tis test 5121233123123', 'period': '4',
                          'db': '1', 'reg_name': '4'})
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                         {'textarea': 'sdas1231233asdtest\nis test1\nis test2\tis test 5123123', 'period': '3',
                          'db': '1', 'reg_name': '4'})
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                         {'textarea': 'sdas1asdd412323asdtest\nis test1\nis test2\tis test 5123123', 'period': '3',
                          'db': '1', 'reg_name': '4'})
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                         {'textarea': 'sdas1123asdtest\nis test1\nis test2\tis test 5123123', 'period': '3', 'db': '1',
                          'reg_name': '4'})
        self.client.post(reverse_lazy('app_word_stat:add_task'),
                         {'textarea': '2312323sdas123asdtest\nis test1\nis test2\tis test 5123123', 'period': '3',
                          'db': '1', 'reg_name': '4'})

        self.client.logout()

        User.objects.get(username='user_is_group')
        self.client.login(username='user_is_group', password='temporary')
        response = self.client.post(reverse_lazy('app_word_stat:api_get_all_task'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_json = json.loads(response.content.decode())

        self.assertEqual(type(response_json), dict)
        self.assertEqual(len(response_json['content']['data']['items_list']), 6)
        self.assertFalse(response_json['content']['err'])
        self.assertEqual(response_json['status'], 200)
