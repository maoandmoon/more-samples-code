import logging
import time

import requests
from celery.utils.log import get_task_logger
from django.utils import timezone
from lxml import etree
from antigate import AntiGate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from work_project.settings import BASE_DIR
from work_project.celery import app
from .models import ModelTask, ModelWordsFile, PERIOD_TYPE_LIST, PERIOD_TYPE_LIST_LANG, DB_TYPE_LIST, \
    DB_TYPE_LIST_LANG, get_type_is_id

logger = get_task_logger(__name__)


class ExceptionWebDriver(Exception):
    """
    Исключение
    """
    pass


class ExceptionWordStat(Exception):
    pass


def html_parser(html_page):
    tree = etree.HTML(html_page)
    items_list = tree.xpath('/html/body/div[2]/div/div/'
                            'div[@class="b-history__data b-history__data_group-by_weekly"]/'
                            'div[3]/table/tbody/tr/td/div/table/tbody/tr')

    for item in items_list:
        total_counts = ''
        for all_i in item.xpath('td[3]/span/text()'):
            total_counts += all_i

        rel_count = ''
        for all_i in item.xpath('td[4]/span/text()'):
            rel_count += all_i

        data_start, data_end = str(item.xpath("td[1]/text()")[0]).split(' - ')
        yield {'data_start': data_start,
               'data_end': data_end,
               'total_counts': int(total_counts),
               'rel_count': float(rel_count.replace(',', '.'))
               }


def exception_decorator(fun):
    """
    Декторатор который игнорирует все исключения
    Пишет ошибки в log

    причина появления: из-за очень большого количества ошибок в selenium,
    этот подход позволяет не дублировать код и обрабатывать ошибки
    :param fun:
    :return:
    """

    def decorator(*args, **kwargs):
        try:
            data = fun(*args, **kwargs)
        except Exception as err:
            # logger.warning(err)
            return False
        return data

    return decorator


class ElementWebDriver:
    """
    Прокси для для selenium element

    Позволяет не обрабатывать ошибки, получать или не получать данные
    """

    def __init__(self, element):
        self.element = element

    @exception_decorator
    def click(self) -> bool:
        """proxy для метода click, но возврашает bool"""
        self.element.click()
        return True

    @exception_decorator
    def send_keys(self, text: str):
        """proxy для метода send_keys"""
        self.element.send_keys(text)

    @exception_decorator
    def get_attribute(self, name: str):
        """proxy для метода get_attribute"""
        return self.element.get_attribute(name)

    @exception_decorator
    def get_text(self):
        return self.element.text

    @exception_decorator
    def get_is_displayed(self):
        return self.element.is_displayed()


class LiteWebDriver:
    """
    Позволяет упростить работу с selenium для минимума

    причина появления: из-за очень большого количества ошибок в selenium,
    этот подход позволяет не дублировать код и обрабатывать ошибки
    """

    def __init__(self):
        self.driver = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self):
        """Запуск бразуер"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def close(self):
        """Выключает бразуер"""
        try:
            self.driver.quit()
        except Exception as err:
            # Если что-то пошло не так
            # logger.warning(err)
            pass

    def restart_driver(self):
        """Перезагружает бразуер"""
        self.close()
        self.start()

    def get(self, url: str):
        """
        Перезоидит по url

        Если вдруг url не валидный отдает False и перезапускает браузер
        (потому что он скорей всего умер после перехода по невалидному url)

        :param url: ссылка на сайт
        :return: статус перехода: True - все хорошо, False - все плохо
        """
        try:
            self.driver.get(url)
        except Exception as err:
            # logger.warning(err)
            self.restart_driver()
            return False
        return True

    def get_element_by_xpath(self, xpath: str):
        """
        Ишет элемент по xpath, если элемент не найден отдает None

        :param xpath:
        :return: отдает элемент или None (если элемент не найден)
        """
        try:
            _element = self.driver.find_element_by_xpath(xpath)

            element = ElementWebDriver(_element)
        except Exception as err:
            # logger.warning(err)
            return None
        return element

    @exception_decorator
    def page_source(self):
        return self.driver.page_source


class WordStat:
    """
    Сбор статистики с Yandex word stat
    """

    LINK_AUTH = 'https://wordstat.yandex.ru/#!/history?words=test'
    LINK_WORD_STAT = 'https://wordstat.yandex.ru/#!/history?'

    def __init__(self, task_id: int):

        self.task_info = ModelTask.objects.filter(id=task_id).select_related().get()
        self.task_info.status = 2
        self.task_info.save()

        self.task_info_period = get_type_is_id(self.task_info.period_type, PERIOD_TYPE_LIST, PERIOD_TYPE_LIST_LANG)
        self.task_db_type = get_type_is_id(self.task_info.db_type, DB_TYPE_LIST, DB_TYPE_LIST_LANG)

        self.word = None
        self.url_period = None
        self.url_db = None
        self.url_region = self.task_info.regions_type

        self.driver = LiteWebDriver()
        self.driver.start()

    def login(self):
        """
        Войти на Yandex
        """
        self.driver.get(self.LINK_AUTH)
        time.sleep(3)
        login = self.driver.get_element_by_xpath('//*[@id="b-domik_popup-username"]')
        login.send_keys('denls.none')  # TODO убрать данные
        password = self.driver.get_element_by_xpath('//*[@id="b-domik_popup-password"]')
        password.send_keys('xt3PwC00')  # TODO убрать данные
        button = self.driver.get_element_by_xpath(
            '/html/body/form/table/tbody/tr[2]/td[2]/div/div[5]/span[1]/input')
        button.click()

    def get_link(self):
        """
        Формирует link для получения статистики по слову

        При формировании добавляються параметры:
         - period: периуд месяц или неделя
         - db: тип устройства
         - regions: регион
         - words: слово или предложение

        :return: отдает link
        """
        link = self.LINK_WORD_STAT

        url_period = self.url_period[0]
        url_db = self.url_db[0]
        url_region = self.url_region

        if url_period is not None:
            link += "period={}&".format(url_period)

        if url_db is not None:
            link += "db={}&".format(url_db)

        if url_region is not None:
            link += "regions={}&".format(url_region)

        link += 'words={}'.format(self.word)
        return link

    def download_captcha(self, url):
        """
        Скачивает картинку с капчей и записывает это в бинарную строку


        TODO добавить обработку ошибок

        :param url: url на картинку с капчей
        :return: картинка в виде бинарной строки
        """
        r_img = requests.get(url=url, stream=True)

        if r_img.status_code != 200:
            return None

        img_bit = b''
        for chunk in r_img.iter_content(1024):
            img_bit += chunk

        if not img_bit:
            return None

        return img_bit

    def captcha_send(self, img_bit):
        """
        Принемает картинку ->
        Отправляет её на "анти капчу" ->
        и отдает результат

        :param img_bit: картинка в виде бинарной строки
        :return: результат распознания
        """
        try:
            captcha_gate = AntiGate('35c9e83daa70e28958154736d1621d2e')  # TODO убрать данные
            captcha_id = captcha_gate.send(img_bit)

            captcha = captcha_gate.get(captcha_id)

            logger.info('captcha_gate get: {}'.format(captcha))

            return captcha
        except Exception as err:
            # logger.warning(err)
            return None

    def captcha_recognise(self, url: str):
        """
        Метот который скачивает капчу и распознает её и отдает результат

        :param url: url на картинку с капчей
        :return: результат распознания
        """
        img_bit = self.download_captcha(url)

        if img_bit is None:
            return

        captcha = self.captcha_send(img_bit)

        if captcha is None:
            return

        return str(captcha)

    def search_captcha(self):
        """
        Метод поиска капчи

        :return:
        """
        captcha = self.driver.get_element_by_xpath(
            '/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[1]/td/img')

        statistics_received = self.driver.get_element_by_xpath('/html/body/div[2]/div/div/div[1]')
        statistics_not_received = self.driver.get_element_by_xpath(
            '/html/body/div[2]/div/div/table/tbody/tr/td[4]/div/div/div')
        if statistics_received is not None or statistics_not_received is not None:

            logger.info('search_captcha, iframe is None')
            return True
        elif captcha is None:
            # logger.info('search_captcha, captcha is None')
            return False
        elif captcha is not None and captcha.get_is_displayed():
            url = captcha.get_attribute('src')

            logger.info('search_captcha, captcha link: {}'.format(url))
            return url

        # logger.info('search_captcha, captcha is None')
        return False

    def complete_captcha(self, url):
        """
        Получает капчу, заполняет её и отправляет на проверку yandex

        :return:
        """

        captcha = self.captcha_recognise(url)
        if captcha is None:
            return False

        captcha_input = self.driver.get_element_by_xpath(
            "/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[2]/td[1]/span/span/input")

        captcha_input.send_keys(captcha)

        captcha_button = self.driver.get_element_by_xpath(
            "/html/body/div[7]/div/div/table/tbody/tr/td/div/form/table/tbody/tr[2]/td[2]/span/input")
        captcha_button.click()

        return True

    def test_captcha(self):
        err = 0
        err_max = 20
        err_search_word_status = 0

        old_time = time.time()

        while err < err_max:
            # self.driver.driver.get_screenshot_as_file('./tmp.png')
            url = self.search_captcha()
            if url is True:
                logger.info('search word: {}'.format(self.word))
                search_word_status = self.search_word()
                logger.info('status search word is {}'.format(search_word_status))
                if search_word_status or err_search_word_status > 3:
                    return True
                err_search_word_status += 1

            elif not url:
                if time.time() - old_time > 60:
                    logger.info('Error refresh page...')
                    raise ExceptionWordStat()
                # logger.info('Screenh')
            else:
                self.complete_captcha(url)
                err += 1
                old_time = time.time()

            # time.sleep()
        # Лучше упать чем продолжать работать
        logger.info('Error test_captcha, refresh chrome')
        raise ExceptionWebDriver("Error test_captcha, refresh chrome")

    def search_word(self):
        element = self.driver.get_element_by_xpath("/html/body/div[2]/div/div/div[1]")

        if element is None:
            return False

        element_text = element.get_text()

        if element_text and element_text.split("«")[-1].replace("»", '') == self.word:
            return True
        else:
            return False

    def get_word_stat(self):
        for i in range(10):
            logger.info('Clear page..')
            self.driver.get('https://yandex.ru')
            self.driver.get(self.get_link())
            logger.info('Go to link: ' + self.get_link())

            try:
                self.test_captcha()
            except ExceptionWordStat:
                continue

            word_data = html_parser(self.driver.page_source())
            return word_data

        logger.info('Error test_captcha, refresh chrome (get_word_stat)')
        raise ExceptionWebDriver("Error test_captcha, refresh chrome")

    def iterator_all_options(self):
        for period in self.task_info_period:
            self.url_period = period
            for db in self.task_db_type:
                self.url_db = db
                for word in [i.word for i in self.task_info.is_words.all()]:
                    if word != ' ' or word:
                        self.word = word
                        yield

    def add_file_name(self, file_url):
        select_file = ModelWordsFile.objects.filter(task_id=self.task_info)
        if select_file.exists():
            select_file.update(date=timezone.now())
        else:
            words_file = ModelWordsFile(task_id=self.task_info, file_name=file_url, date=timezone.now())
            words_file.save()

        self.task_info.status = 3
        self.task_info.save()

    def main(self):
        data_all = []

        for _ in range(3):
            self.login()

            for _ in self.iterator_all_options():
                logger.info(
                    'w: {}, r: {}, d: {}, p: {}'.format(self.word, self.url_region, self.url_db[1], self.url_period[1]))

                try:
                    data_r = self.get_word_stat()
                except ExceptionWebDriver:
                    logger.info('Error test_captcha, refresh chrome (main)')
                    self.driver.close()
                    continue

                for i in data_r:
                    # print(self.word, i)
                    data_all.append([self.word, i['data_start'], i['data_end'], i['total_counts'], i['rel_count'],
                                     self.task_info.get_regions_type(), self.url_db[1], self.url_period[1]])

            break

        self.driver.close()

        # for i in data_all:
        #     print(i)

        # TODO исправить запись
        file_url = BASE_DIR + "\\static\\app_word_stat\\tmp\\task_id_{}.csv".format(self.task_info.id)

        with open(file_url, 'w') as f:
            f.write("Слово;Период начало;Период конец;Абсолютное;Относительное;Регион;Тип;Период;\n")

            for i in data_all:
                f.write(';'.join([str(item) for item in i]) + ';\n')

        self.add_file_name(file_url)


@app.task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def get_word_stat(task_id):
    word_stat = WordStat(task_id)
    word_stat.main()
