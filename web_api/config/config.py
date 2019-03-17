"""
Configuration module
"""

import yaml
from logger import logger

DEFAULT = "DEFAULT"
TEST = "TEST"
DEV = "DEV"

log = logger.create_logger(__name__)


class Singleton(type):
    """Singleton metaclass to be used as a class for all the singleton classes"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(object):
    """Config that reads the configuration from given yaml and section"""
    __metaclass__ = Singleton

    def __init__(self, config_file, section=DEFAULT):
        self.__config_file = config_file
        self.__section = section
        self.__config = self.__read_config()
        self.__add_attrs()

    def __read_config(self):
        log.info(
            "Read configuration from file: {0} using section: {1}".format(
                self.__config_file,
                self.__section
            )
        )
        with open(self.__config_file, 'r') as yamlfile:
            content = yaml.load(yamlfile)
            if content:
                return content
        return {}

    def __add_attrs(self):
        section = self.__config.get(self.__section, {})
        for key, value in section.items():
            setattr(self, key, value)