import configparser
import logging.config
import shutil
import os.path
import os

_CONFIG_FILE = 'ploev.ini'


def _load_config():
    config = configparser.ConfigParser()
    if not config.read(_CONFIG_FILE):
        default_ini_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), _CONFIG_FILE)
        shutil.copy(default_ini_path, os.getcwd())
        config.read(_CONFIG_FILE)
    return config


CONFIG = _load_config()

_LOG_CONFIG = {
    'version': 1,
    'handlers': {
        'fileHandler':{
            'class': 'logging.FileHandler',
            'formatter': 'myFormatter',
            'filename': 'ploev.log',
            'mode': CONFIG['LOGGER']['mode']
        }
    },
    'loggers': {
        'ppt': {
            'handlers': ['fileHandler'],
            'level': CONFIG['LOGGER']['level'],
        }
    },
    'formatters':{
        'myFormatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
}


logging.config.dictConfig(_LOG_CONFIG)
