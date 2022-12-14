from NikGapps.Web.Requests import Requests


class AndroidDump:
    def __init__(self):
        self.host = "https://dumps.tadiphone.dev/dumps/google/"
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_host(self):
        return self.host
