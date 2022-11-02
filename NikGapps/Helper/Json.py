from urllib.request import urlopen
import json


class Json:

    @staticmethod
    def print_json_dict(json_dict):
        print(json.dumps(json_dict, indent=2, sort_keys=True))

    @staticmethod
    def write_dict_to_file(json_dict, file_name):
        try:
            with open(file_name, 'w') as file:
                json_dumps_str = json.dumps(json_dict, indent=4, sort_keys=True)
                print(json_dumps_str, file=file)
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def read_dict_from_file(file_name):
        try:
            with open(file_name, 'r') as file:
                json_dict = json.load(file)
                return json_dict
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def read_from_url(url, beautify=False):
        response = urlopen(url)
        data_json = json.loads(response.read())
        # print(data_json["manager"]["url"])
        # print(data_json[0]["url"])
        # print(len(data_json))
        # print(data_json)
        # for i in range(0, len(data_json)):
        #     print(data_json[i]["url"])
        return data_json

    @staticmethod
    def print_from_url(url, beautify=False):
        data_json = Json.read_from_url(url, beautify)
        if beautify:
            data_json = json.dumps(data_json, indent=4, sort_keys=True)
        print(data_json)

# https://api.github.com/repos/nikgapps/config/pulls/257/files
# Json.read_from_url("https://mirror.codebucket.de/vanced/api/v1/latest.json")
# Json.read_from_url("https://api.github.com/repos/nikgapps/config/pulls")
# Json.print_from_url("https://raw.githubusercontent.com/nikgapps/tracker/main/count.json", True)
