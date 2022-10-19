import json

import requests


class Requests:

    @staticmethod
    def get(url, params, headers):
        return requests.get(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def put(url, params, headers):
        return requests.put(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def patch(url, params, headers):
        return requests.patch(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def post(url, params, headers):
        return requests.post(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def get_text(url):
        return requests.get(url).text
