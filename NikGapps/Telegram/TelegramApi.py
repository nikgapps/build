from NikGapps.Web.Requests import Requests


class TelegramApi:

    def __init__(self, token=""):
        self.token = token
        self.base = "https://api.telegram.org"
        self.chat_id = ""
        self.message_id = None
        self.msg = None

    def send_message(self, text, chat_id=None):
        if chat_id is None:
            chat_id = self.chat_id
        if text is None or str(text).__eq__(""):
            print("No text to send")
            return None
        url = f"{self.base}/bot{self.token}/sendMessage?chat_id={chat_id}&text={text}"
        r = Requests.get(url)
        response = r.json()
        if response["ok"]:
            self.message_id = response["result"]["message_id"]
            self.msg = text
        return response

    def message(self, text, chat_id=None):
        if chat_id is None:
            chat_id = self.chat_id
        if self.message_id is None:
            return self.send_message(text, chat_id)
        if text is None or str(text).__eq__(""):
            print("No text to send")
            return None
        text = self.msg + "\n" + text
        url = f"{self.base}/bot{self.token}/editMessageText?chat_id={chat_id}&message_id={self.message_id}&text={text}"
        r = Requests.get(url)
        response = r.json()
        if response["ok"]:
            self.msg = response["result"]["text"]
        return response
