import yaml
from app import app

DEFAULT = "DEFAULT"
TEST = "TEST"
DEV = "DEV"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(object):
    __metaclass__ = Singleton

    def __init__(self, config_file, section=DEFAULT):
        self.__config_file = config_file
        self.__section = section
        self.__config = self.__read_config()
        self.__add_attrs()

    def __read_config(self):
        with open(self.__config_file, 'r') as yamlfile:
            content = yaml.load(yamlfile)
            if content:
                return content
        return {}

    def __add_attrs(self):
        section = self.__config.get(self.__section, {})
        for key, value in section.items():
            setattr(self, key, value)


def main():

    config = Config('config.yaml', section='DEFAULT')

    app.run(config.WEBSERVER['HOST'], config.WEBSERVER['PORT'], config.WEBSERVER['DEBUG'])


if __name__ == '__main__':
    main()
