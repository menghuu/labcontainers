#!/usr/bin/env python3

import sqlite3
from utils import _add_lab_user, _init_lab_db
import configparser
import pylxd
import os

if __name__ == '__main__':
    client = pylxd.Client()
    default_image_fingerprint = client.images.all()[0].fingerprint 
    ip_start =  '10.18.242.2/24'
    port_start = '6100' 
    nobody = 'nobody'

    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'ip_start': ip_start,
        'port_start': str(port_start),
        'default_image_fingerprint': default_image_fingerprint,
        'nobody': nobody
    }
    current_path = os.path.split(os.path.abspath(__file__))[0]
    db_path = os.path.join(current_path, 'lab.db')
    config.set('DEFAULT', 'db_path', db_path)
    config['develop'] = {
        'db_path' : db_path
    }
    with open(os.path.join(current_path, 'config.ini'), 'w') as f:
        config.write(f)

    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path) # create db
    _init_lab_db(conn)   # create db structure 
    #_add_lab_user('root', 'root', conn) # add sample user
    users = [
                ('root', 'root'),
            ]
    for username, password in users:
        _add_lab_user(username, password, conn)


