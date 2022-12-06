import Config
from NikGapps.Web.Requests import Requests


class TelegramApi:

    def __init__(self, token=Config.TELEGRAM_BOT_TOKEN):
        self.token = token
        self.base = "https://api.telegram.org"
        # self.chat_id = Config.TELEGRAM_CHAT_ID if Config.NIKGAPPS_CHAT_ID is None else Config.NIKGAPPS_CHAT_ID
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.message_thread_id = Config.MESSAGE_THREAD_ID
        self.message_id = None
        self.msg = None

    def send_message(self, text, chat_id=None):
        if self.token is None:
            return None
        if chat_id is None:
            chat_id = self.chat_id
        if text is None or str(text).__eq__(""):
            print("No text to send")
            return None
        for i in '_*[]()~`>#+-=|{}.!':
            text = text.replace(i, "\\" + i)
        url = f"{self.base}/bot{self.token}/sendMessage" \
              f"?chat_id={chat_id}" \
              f"&text={text}" \
              f"&parse_mode=MarkdownV2" \
              + (f"&message_thread_id={self.message_thread_id}" if self.message_thread_id is not None else "")
        r = Requests.get(url)
        response = r.json()
        if response["ok"]:
            self.message_id = response["result"]["message_id"]
            self.msg = text
        return response

    def message(self, text, chat_id=None):
        if self.token is None:
            return None
        if chat_id is None:
            chat_id = self.chat_id
        if self.message_id is None:
            return self.send_message(text, chat_id)
        if text is None or str(text).__eq__(""):
            print("No text to send")
            return None
        text = self.msg + "\n" + text
        for i in '_*[]()~`>#+-=|{}.!':
            text = text.replace(i, "\\" + i)
        url = f"{self.base}/bot{self.token}/editMessageText" \
              f"?chat_id={chat_id}" \
              f"&message_id={self.message_id}" \
              f"&text={text}" \
              f"&parse_mode=MarkdownV2" \
              + (f"&message_thread_id={self.message_thread_id}" if self.message_thread_id is not None else "")
        r = Requests.get(url)
        response = r.json()
        if response["ok"]:
            self.msg = response["result"]["text"]
        return response

    def reset_message(self):
        self.message_id = None
        self.msg = None
