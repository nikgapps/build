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
        self.last_msg = None

    def message(self, text, chat_id=None, replace_last_message=False, escape_text=True):
        if self.token is None:
            return None
        if chat_id is None:
            chat_id = self.chat_id
        if text is None or str(text).__eq__(""):
            print("No text to send")
            return None
        if escape_text:
            for i in '[]()~`>#+-=|{}.!':
                text = text.replace(i, "\\" + i)
        sending_text = text
        if self.message_id is not None:
            sending_text = self.msg.replace(self.last_msg, text) if replace_last_message else (self.msg + "\n" + text)
        url = self.get_url(chat_id, sending_text)
        r = Requests.get(url)
        if r.status_code != 200:
            print(f"Error sending message: {r.json()}")
            return None
        response = r.json()
        if response["ok"]:
            self.last_msg = text
            self.msg = sending_text
            self.message_id = response["result"]["message_id"]
        return response

    def get_url(self, chat_id, sending_text):
        return f"{self.base}/bot{self.token}/" \
            + (f"sendMessage?" if self.message_id is None else f"editMessageText?&message_id={self.message_id}") \
            + f"&chat_id={chat_id}" \
            + f"&parse_mode=MarkdownV2" \
            + f"&text={sending_text}" \
            + (f"&message_thread_id={self.message_thread_id}" if self.message_thread_id is not None else "")

    def delete_message(self, message_id=None, chat_id=None):
        if self.token is None:
            return None
        if chat_id is None:
            chat_id = self.chat_id
        if message_id is None:
            message_id = self.message_id
        if message_id is None:
            return None
        url = f"{self.base}/bot{self.token}/deleteMessage" \
              f"?chat_id={chat_id}" \
              f"&message_id={str(message_id)}"
        r = Requests.get(url)
        response = r.json()
        return response

    def reset_message(self):
        self.message_id = None
        self.msg = None
