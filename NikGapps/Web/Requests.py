import json

import requests


class Requests:

    @staticmethod
    def get(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.get(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def put(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.put(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def patch(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.patch(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def post(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.post(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def get_text(url):
        return requests.get(url).text
