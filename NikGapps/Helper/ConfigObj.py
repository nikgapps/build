class ConfigObj:

    def __init__(self, key, value, configdesc=None):
        self.key = key
        self.value = value
        self.description = None
        if configdesc is not None:
            self.description = configdesc

    def get_string(self):
        config_str = ""
        if self.description is not None:
            config_str = self.description + "\n"
        config_str += self.key + "=" + str(self.value) + "\n\n"
        return config_str

