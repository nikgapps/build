import time

import requests
import yaml

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
        self.urls = {}
        self.changelog = None

    def message(self, text, chat_id=None, replace_last_message=False, escape_text=True, parse_mode="markdown",
                ur_link=None):
        if self.token is None:
            return None
        if chat_id is None:
            chat_id = self.chat_id
        if text is None or str(text).__eq__(""):
            print("No text to send")
            return None
        if escape_text:
            for i in '_*[]~`>+=|{}':
                text = text.replace(i, "\\" + i)
        sending_text = text
        if self.message_id is not None:
            sending_text = self.msg.replace(self.last_msg, text) if replace_last_message else (self.msg + "\n" + text)
        data = {
            "chat_id": chat_id,
            "text": f"{sending_text}",
            "parse_mode": f"{parse_mode}",
            "disable_web_page_preview": True
        }
        if self.message_thread_id is not None:
            data["message_thread_id"] = self.message_thread_id
        url = f"{self.base}/bot{self.token}/sendMessage"
        if self.message_id is not None:
            data["message_id"] = self.message_id
            url = f"{self.base}/bot{self.token}/editMessageText"
        if ur_link is not None:
            ur_link: dict
            for key in ur_link:
                self.urls[key] = ur_link[key]
        if len(self.urls) > 0:
            row_list = []
            inline_list = []
            max_col = 1 if len(self.urls) > 1 else len(self.urls)
            for count, key in enumerate(self.urls):
                inline_list.append({"text": key, "url": self.urls[key]})
                if count == max_col:
                    row_list.append(inline_list)
                    inline_list = []
            if len(inline_list) > 0:
                row_list.append(inline_list)
            data["reply_markup"] = {
                "inline_keyboard": [
                    row for row in row_list
                ]
            }
        r = requests.post(url, json=data)
        response = r.json()
        if r.status_code != 200:
            print(f"Error sending message: {response}")
            if r.status_code == 429:
                print(f"Sleeping for {response['parameters']['retry_after']} seconds")
                time.sleep(response['parameters']['retry_after'])
            else:
                return None
        if response["ok"]:
            self.last_msg = text
            self.msg = sending_text
            self.message_id = response["result"]["message_id"]
        return response

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

    def get_latest_changelog_message(self, changelog=None):
        if changelog is not None:
            self.changelog = changelog
            with open(self.changelog, 'r') as stream:
                try:
                    msg = ""
                    for date in yaml.safe_load(stream):
                        msg += f"*New Release is up - {date['date']}*\n\n"
                        msg += f"Changelog:\n"
                        for item in date['changes']:
                            msg += f"- {item['item']}\n"
                        msg += f"\n"
                        msg += f"*Note: *\n"
                        msg += "- You can always take a backup and dirty flash the gapps, if you run into issues, you should try clean flashing the gapps.\n"
                        msg += "if you have any problem feel free to reach us @NikGappsGroup\nHappy Flashing!"
                        break
                    return msg
                except yaml.YAMLError as exc:
                    print(exc)
        return None

    def reset_message(self):
        self.message_id = None
        self.msg = None
        self.urls = {}
