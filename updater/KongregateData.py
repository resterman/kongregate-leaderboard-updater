from queue import Queue
from threading import Thread

import requests


class ActionThread(Thread):
    def __init__(self, results, callback):
        Thread.__init__(self)

        self.results = results
        self.callback = callback

    def run(self):
        while True:
            user = self.results.get()
            self.callback(user)
            self.results.task_done()


class LoaderThread(Thread):
    def __init__(self, urls, results):
        Thread.__init__(self)

        self.session = requests.Session()
        self.urls = urls
        self.results = results

    def run(self):
        while True:
            url = self.urls.get()

            try:
                response = self.session.get(url)

                users = response.json().get(KongregateData.USER_KEY)
                for user in users:
                    self.results.put(user)

            except requests.exceptions.ConnectionError:
                self.urls.put_nowait(url)
            except requests.exceptions.RequestException as e:
                print("Unexpected error: ({}, {})".format(e.errno, e.strerror))

            self.urls.task_done()


class KongregateData(object):
    URL = 'http://api.kongregate.com/api/user_info.json?user_ids='
    USERS_PER_REQUEST = 50
    USER_KEY = 'users'

    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.urls = Queue()
        self.results = Queue()
        self.generate_urls()

    def __str__(self):
        return "[KongregateData from:{} to:{}]".format(self.start, self.end)

    def generate_urls(self):
        i = self.start

        while i <= self.end:
            user_ids = list(range(i, i + KongregateData.USERS_PER_REQUEST))
            url = '{URL}{QUERY}'.format(URL=KongregateData.URL, QUERY=','.join([str(user_id) for user_id in user_ids]))
            self.urls.put_nowait(url)

            i += KongregateData.USERS_PER_REQUEST

    def run(self, threads, callback):
        """
        Start downloading data and processing it

        :param threads:		number of threads to open
        :param callback:	callback function to be called for every user
        """
        for i in range(threads):
            t = LoaderThread(self.urls, self.results)
            t.daemon = True
            t.start()

        t = ActionThread(self.results, callback)
        t.daemon = True
        t.start()

        self.urls.join()
        self.results.join()
