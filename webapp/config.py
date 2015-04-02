import os
import configparser

config = None


def init(conf_file='./scheduler.conf'):
    global config
    try:
        file_name = os.environ['CALDAV_MW_CONFIG']
    except KeyError:
        file_name = conf_file
    parser = configparser.SafeConfigParser()
    parser.read(file_name)
    config = parser


def get_config(self):
    global config
    if config is None:
        init()
    return config
