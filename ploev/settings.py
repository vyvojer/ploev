# ploev
# Copyright (C) 2017 Alexey Londkevich <vyvojer@gmail.com>

# ploev is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ploev is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Class for settings """

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
