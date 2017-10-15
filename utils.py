# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 15:22:27 2017

@author: m
"""
import collections
import os
import re
import uuid
from io import StringIO
import hashlib
from base64 import b64decode, b64encode

from texttable import Texttable

ContainerState = collections.namedtuple("ContainerState", "belongs_to, status_code")

def _print_details(details):
    header = list(details.keys())
    _tmp = []
    for k in details.keys():
        _tmp.append(details[k])
    cols = list(map(list, list(zip(*_tmp))))
    table = Texttable()
    table.header(header)
    table.add_rows(cols, header=False)
    print(table.draw())

def _generate_container_name(username, container_name=None):
    if container_name is None:
        container_name = str(uuid.uuid1()).split('-')[0]
        container_name = '{}-lxc-{}'.format(username , container_name)
    elif container_name.startswith('{}-lxc'.format(username)):
        container_name = container_name
    else:
        container_name = '{}-lxc-{}'.format(username , container_name)
    _check_container_name(container_name)
    return container_name

def gen_keys(key="", name='unknown'):
    from paramiko import SSHException
    from paramiko.rsakey import RSAKey

    """
    生成公钥 私钥
    """
    output = StringIO()
    sbuffer = StringIO()
    key_content = {}
    if not key:
        try:
            key = RSAKey.generate(2048)
            key.write_private_key(output)
            private_key = output.getvalue()
        except IOError:
            raise IOError('gen_keys: there was an error writing to the file')
        except SSHException:
            raise SSHException('gen_keys: the key is invalid')
    else:
        private_key = key
        output.write(key)
        try:
            key = RSAKey.from_private_key(output)
        except SSHException as e:
            raise SSHException(e)

    for data in [key.get_name(),
                    " ",
                    key.get_base64(),
                    " %s@%s" % (name, os.uname()[1])]:
        sbuffer.write(data)
    public_key = sbuffer.getvalue()
    key_content['public_key'] = public_key
    key_content['private_key'] = private_key
    return key_content


def _check_username(username, regex=None, cursor=None):
    if regex == None:
        regex = re.compile(r'^[a-zA-Z_]{1}[\w]{1,32}$')
    _result = regex.findall(username)
    if len(_result) != 1:
        raise ValueError('illegal username')

def _check_container_name(container_name, regex=None):
    if regex == None:
        regex = re.compile(r'^[a-zA-Z]{1}[-\w]{1,32}$')
    _result = regex.findall(container_name)
    if len(_result) != 1:
        raise ValueError('illegal container name')

def _check_password(passwd):
    if ( len(passwd) > 64 ) or (len(passwd)<5):
        raise ValueError('password too long, (>5 and <64)')



def _iptables_ports(containers_ip, port_start=61000, ip_start='10.18.242.2/24'):
    import collections
    if not isinstance(containers_ip, collections.Iterable) or isinstance(containers_ip, str):
        pass
        containers_ip = [containers_ip]
    ports = []
    for container_ip in containers_ip:
        ports.append(_iptables_port(
            container_ip, port_start, ip_start
        ))
    return ports

def _iptables_port(container_ip, port_start=61000, ip_start='10.18.242.2/24'):
    pattern_mask = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-4]|2[0-4][0-9]|[01]?[0-9][0-9]?)/([012]{1}\d{1})|(3[012]{1})\b"
    pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-4]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    if container_ip is None:
        return None
    if not re.match(pattern, container_ip):
        return None
        raise ValueError('{} is not valid ip address with mask'.format(container_ip))

    if port_start <= 1024:
        raise ValueError('{} is a privilege port, currently we cannot support those port')

    if not re.match(pattern_mask, ip_start):
        raise ValueError("{} is not valid ip address")

    _mask = int(ip_start[ip_start.rfind('/'):][1:])
    #_mask_int = int(('{:1>'+'{}'.format(_mask) + '}').format('') + ('{:0>' + '{}'.format(32-_mask) + '}').format(''),2)
    _mask_int = int(_mask*'1' + (32-_mask)*'0', 2)
    _ip = ip_start[:ip_start.rfind('/')]
    _ip_int = int(''.join(['{:0>8}'.format(bin(int(i))[2:]) for i in _ip.split('.')]), 2)

    container_ip_int = int(''.join(['{:0>8}'.format(bin(int(i))[2:]) for i in container_ip.split('.')]), 2)
    if (container_ip_int & _mask_int) != (_ip_int & _mask_int):
        raise ValueError('container_ip is not at the same subnet with ip_start')
    port = port_start + container_ip_int - _ip_int
    return port 


def _owning_containers_name(username, conn):
    cursor = conn.cursor()
    cursor.execute('select container_name from lab_containers where belongs_to_username = ?;', (username,))
    names  = cursor.fetchall()
    cursor.close()
    if names == []:
        return []
    else:
        return list(list(zip(*names))[0])

def _container_state(container_name, conn, client):
    belongs_to = None
    status_code = None

    cursor = conn.cursor()
    cursor.execute('select belongs_to_username from lab_containers where container_name = ?;', (container_name,))
    result_from_db = cursor.fetchone()


    if result_from_db is None:
        belongs_to = None
    elif len(result_from_db)==1:
        belongs_to = result_from_db[0]
    else:
        raise RuntimeError('{} own the same container {}'.format(result_from_db, container_name))

    if client.containers.exists(container_name):
        status_code = client.containers.get(container_name).status_code
    else:
        status_code = None
    return ContainerState(belongs_to=belongs_to, status_code=status_code)
def _images_detail(client):
    from collections import OrderedDict
    details = OrderedDict([
        ('name', []),
        ('description', []),
        ('fingerprint',[])
    ])
    images =  client.images.all()
    for image in images:
        try:
            details['name'].append(image.aliases[0].get('name', None))
        except:
            details['name'].append(None)
        details['fingerprint'].append(image.fingerprint)
        details['description'].append(image.properties.get('description', None))
    return details

def _merge_details(details_one, details_two):
    for k in details_one:
        details_one[k] += details_two[k]
    return details_one 

def _add_lab_user(username, password, conn):
    if isinstance(password, bytes):
        pass
    elif isinstance(password, str):
        password = password.encode('utf-8')
    else:
        raise ValueError('input password should be bytes or password')
    cursor = conn.cursor()
    cursor.execute('select * from lab_users where username = ?;', (username,))
    if cursor.fetchone() is None:
        salt = os.urandom(12)
        # print('\nin add_lab_user, salt is ', b64encode(salt).decode())
        password_after = hashlib.sha256(password+salt).hexdigest()
        # print('in add_lab_user, password_after is ', password_after)
        cursor.execute('insert into lab_users(username, password, salt) values(?,?,?);', (username, password_after, b64encode(salt).decode('utf-8')))
        conn.commit()
        cursor.close()
        return True 
    else:
        return False 

def _del_lab_user(username, conn, client):
    cursor = conn.cursor()
    cursor.execute('select * from lab_users where username = ?;', (username,))
    if cursor.fetchone() is None:
        return 'no lab_user {}'.format(username)
    cursor.execute('delete from lab_users where username = ?;',(username,))
    conn.commit()
    # to-do: delete the containers belong to the user which will be deleted
    # cursor.execute('select container_name from lab_containers where belongs_to_username = ?;', (username,))
    # containers_name = cursor.fetchone()


def _check_login(username, password, conn):
    if isinstance(password, bytes):
        pass
    elif isinstance(password, str):
        password = password.encode('utf-8')
    else:
        raise ValueError('input password should be bytes or str')
    cursor = conn.cursor()
    cursor.execute('select salt from lab_users where username = ?;',(username,))
    salt = cursor.fetchone()
    if salt is None:
        return False
    # print('in check_login, salt is ', salt[0])
    salt = b64decode(salt[0].encode('utf-8'))
    password_after = hashlib.sha256(password + salt).hexdigest()
    # print('in check_login, password_after is ', password_after)

    cursor.execute('select * from lab_users where username = ? and password=?;', (username, password_after))

    if cursor.fetchone() is None:
        return False
    else:
        return True



def _init_lab_db(conn):
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE lab_users'+\
        '(uid INTEGER PRIMARY KEY AUTOINCREMENT,'+\
            'username TEXT NOT NULL UNIQUE,'+\
            'password TEXT NOT NULL,'+\
            'salt TEXT NOT NULL);'
        )
    cursor.execute(
            'CREATE TABLE lab_containers(\
                container_name TEXT NOT NULL PRIMARY KEY UNIQUE,\
                belongs_to_username TEXT NOT NULL,\
                FOREIGN KEY(belongs_to_username) REFERENCES \
                    lab_users(username)\
                );')
    conn.commit()
