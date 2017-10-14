#!/usr/bin/env python3

import sqlite3
from utils import _add_lab_user
import configparser
import pylxd

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/home/m/projects/labcontainers/config.ini')
    ip_start = config['default'].get('ip_start')
    port_start = config['default'].getint('port_start')
    default_image_fingerprint = config['default'].get('default_image_fingerprint')
    db_path = config['default'].get('db_path')
    nobody = config['default'].get('nobody', 'nobody')
    client = pylxd.Client()
    conn = sqlite3.connect(db_path)
    _add_lab_user('root', 'root', conn)