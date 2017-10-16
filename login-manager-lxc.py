#!/usr/bin/env python3
import cmd
import configparser
import getpass
import json
import subprocess
import sys
import os
import pylxd

from manager_lxc_utils import (_change_container_key, _container_state,
                               _create_container, _delete_container,
                               _launch_container, _restart_container,
                               _start_container, _stop_container)
from prompt import Prompt
from utils import (ContainerState, _check_container_name, _check_login,
                   _check_password, _generate_container_name, _images_detail,
                   _owning_containers_name, gen_keys)


def _login(conn):
    while True:
        username = input('please input your username: ').strip()
        password = getpass.getpass('please input you password: ')
        if not _check_login(username, password, conn):
            print('wrong password or the password is not associated with the {username}'.format(username=username))
            continue
        else:
            break
    return username



if __name__ == '__main__':
    current_path = os.path.split(os.path.abspath(__file__))[0]
    config = configparser.ConfigParser()
    config.read(os.path.join(current_path, 'config.ini'))
    ip_start = config['DEFAULT'].get('ip_start')
    port_start = config['DEFAULT'].getint('port_start')
    default_image_fingerprint = config['DEFAULT'].get('default_image_fingerprint')
    db_path = config['DEFAULT'].get('db_path')
    lxc_nvidia_profile = config['DEFAULT'].get('lxc_nvidia_profile') 
    nobody = config['DEFAULT'].get('nobody', 'nobody')
    client = pylxd.Client()
    prompt = Prompt(db_path, client, port_start, ip_start, default_image_fingerprint, profiles=[lxc_nvidia_profile,'default'], nobody=nobody)
    prompt.cmdloop()
    exit()
