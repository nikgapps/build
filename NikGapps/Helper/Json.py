from urllib.request import urlopen
import json


class Json:
    @staticmethod
    def read_from_url(url):
        response = urlopen(url)
        data_json = json.loads(response.read())
        # print(data_json)
        # print(json.dumps(data_json, indent=4, sort_keys=True))
        # print(data_json["manager"]["url"])
        # print(data_json[0]["url"])
        # print(len(data_json))
        for i in range(0, len(data_json)):
            print(data_json[i]["url"])
        return data_json

# https://api.github.com/repos/nikgapps/config/pulls/257/files
# Json.read_from_url("https://mirror.codebucket.de/vanced/api/v1/latest.json")
Json.read_from_url("https://api.github.com/repos/nikgapps/config/pulls")
