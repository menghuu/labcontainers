import collections
import json

import pylxd

from lab_exceptions import LabContainerStateException
from utils import (_check_container_name, _check_password, _check_username,
                   _container_state, _iptables_port, gen_keys)

ContainerState = collections.namedtuple("ContainerState", "belongs_to, status_code")

import os



def _start_container(container_name, username, conn, client):

    if username is None:
        raise ValueError('username should not be None')
    if container_name is None:
        raise ValueError('container_name should not be None')

    belongs_to, status_code = _container_state(container_name, conn, client)
    acceptable_code = [103, 106]

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        pass
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        pass
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你, 而且处于runing 和 starting 状态
        return
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你,
        client.containers.get(container_name).start(wait=True)
        return

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log status_code belongs_to username
    raise LabContainerStateException(
        container_name,status_code, belongs_to, username, 'start'
    )

def _stop_container(container_name, username, conn, client):

    if container_name is None:
        raise ValueError('container_name should not None')
    if username is None:
        raise ValueError('username should not None')
    username = username.strip()
    container_name = container_name.strip()

    acceptable_code = [102]

    belongs_to, status_code = _container_state(container_name, conn, client)

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在,应该记录一下
        pass
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        # log
        pass
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你，而且已经停止了
        return
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你，并且没有停止
        client.containers.get(container_name).stop(wait=True)
        return

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在，应该记录一下
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log status_code belongs_to username
    raise LabContainerStateException(
        container_name, status_code, belongs_to, username, 'stop'
    )

def _create_container(container_name, username, conn, client,\
        base_image_fingerprint, profiles=None):
    if username is None or username is '':
        raise RuntimeError('username should not None')
    # container_name = container_name or _generate_container_name(username, )
    if isinstance(profiles, list):
        profiles = list(profiles)
    else:
        profiles = ['default']

    machine = {
               'name': container_name, 'architecture': '2', \
               'profiles': profiles, 'ephemeral': False, \
               'source': {'type': 'image', \
                          'fingerprint': base_image_fingerprint\
                         }\
              }
    belongs_to, status_code = _container_state(container_name, conn, client)

    acceptable_code = ['not_import']

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        client.containers.create(config=machine, wait=True)
        cursor = conn.cursor()
        cursor.execute('insert into lab_containers(container_name, belongs_to_username) values(?, ?);', (container_name, username))
        conn.commit()
        return
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，
        # log 数据库和 lxc 不同步
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，
        # log 数据库和 lxc 不同步
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        client.containers.create(config=machine, wait=True)
        return
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你,什么状态并不重要
        return
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你,什么状态不重要
        return
    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在，
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log status_code belongs_to username
    raise LabContainerStateException(
        container_name, status_code, belongs_to, username, 'create'
    )

def _delete_container(container_name, username, conn, client, enforce=False):
    if container_name is None:
        raise ValueError('container_name should not None')
    if username is None:
        raise ValueError('username should not None')

    belongs_to, status_code = _container_state(container_name, conn, client)

    acceptable_code = [103] # running

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        pass
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在, 应该记录
        # log 不同步
        cursor = conn.cursor()
        cursor.execute('delete from lab_containers where belongs_to = ?;', (container_name,))
        conn.commit()
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你,并且正在运行
        if enforce:
            _stop_container(container_name, username, conn, client)
            _delete_container(container_name, username, conn, client, enforce)
            return
        else:
            # 应该记录一下
            pass
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你
        client.containers.get(container_name).delete(wait=True)
        cursor = conn.cursor()
        cursor.execute('delete from lab_containers where container_name=?;',(container_name,))
        conn.commit()
        return

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass

    # log status_code
    raise LabContainerStateException(
        container_name, status_code, belongs_to, username, 'delete'
    )

def _launch_container(container_name, username, conn,
        client, base_image_fingerprint, profiles=None):
    """launch the container
        if the container name is same as you input, it will be *not* re-create.
        if the container is running, just return
        if the container is stopped, start and return
        if the container is not exist, create and start it
    """
    if container_name is None:
        raise ValueError('container_name should not None')
    if username is None:
        raise ValueError('username should not None')

    belongs_to, status_code = _container_state(container_name, conn, client)

    acceptable_code = [103]

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        _create_container(
            container_name, username, conn, client, base_image_fingerprint,
            profiles
        )
        _start_container(container_name, username, conn, client)
        return
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        _create_container(
            container_name, username, conn, client, base_image_fingerprint
        )
        _start_container(container_name, username, conn, client)
        return
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你,并且正在运行
        return
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你,但是没有运行
        _start_container(container_name, username, conn, client)
        return

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在，应该记录一下
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log
    raise LabContainerStateException(
        container_name, status_code, belongs_to, username, 'launch'
    )

def _restart_container(container_name, username, conn, client):
    if container_name is None:
        raise ValueError('container_name should not None')
    if username is None:
        raise ValueError('username should not None')

    belongs_to, status_code = _container_state(container_name, conn, client)
    acceptable_code = [103, 106]

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        pass
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        pass
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你, 而且处于runing 和 starting 状态
        _stop_container(container_name, username, conn, client)
        _start_container(container_name, username, conn, client)
        return
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你, 可以运行
        _start_container(container_name, username, conn, client)
        return

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log status_code belongs_to username
    raise LabContainerStateException(
        container_name, status_code, belongs_to, username, 'restart'
    )

def _change_container_password(container_name, username, conn, client, password):
    if container_name is None:
        raise ValueError('container_name should not None')
    if username is None:
        raise ValueError('username should not None')

    belongs_to, status_code = _container_state(container_name, conn, client)
    acceptable_code = [103]

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        pass
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        pass
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你,且在运行
        container = client.containers.get(container_name)
        container.execute(['/bin/bash', '-c', 'echo "ubuntu:{}" | chpasswd'.format(password)])
        return
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你,但是没有运行
        pass

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log status_code belongs_to username
    raise LabContainerStateException(
        container_name, status_code, belongs_to, username, 'change_container_password'
    )
def _change_container_key(container_name, username, conn, client, private_key):
    if container_name is None:
        raise ValueError('container_name should not None')
    if username is None:
        raise ValueError('username should not None')

    belongs_to, status_code = _container_state(container_name, conn, client)
    acceptable_code = [103]

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        pass
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        pass
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你,且在运行
        container = client.containers.get(container_name)
        keys = gen_keys(private_key, username)
        container.files.put('/home/ubuntu/.ssh/authorized_keys', keys['public_key'])
        container.execute(['/bin/chown', 'ubuntu:ubuntu', '/home/ubuntu/.ssh/authorized_keys'])
        return keys
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你,但是没有运行
        pass

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log status_code belongs_to username
    raise LabContainerStateException(
        container_name, status_code, belongs_to, username, 'restart'
    )

def _container_details(container_name, username, conn, client, port_start=61000, ip_start='10.18.242.2/24'):
    if username is None:
        raise ValueError('username should not be None')
    if container_name is None:
        raise ValueError('container_name should not be None')
    belongs_to, status_code = _container_state(container_name, conn, client)
    acceptable_code = ["not-important"]

    if belongs_to is None and status_code is None:
        # 不属于任何人，也不存在
        pass
    elif belongs_to is None and status_code in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass
    elif belongs_to is None and status_code not in acceptable_code:
        # 不属于任何人，但是存在，应该记录一下
        # log 数据库和 lxc 不同步
        pass

    if belongs_to == username and status_code is None:
        # 属于你，但是不存在
        return _container_details_(
            container_name, client, port_start, ip_start
        )
        pass
    elif belongs_to == username and status_code in acceptable_code:
        # 属于你,而且存在
        return _container_details_(
            container_name, client, port_start, ip_start
        )
    elif belongs_to == username and status_code not in acceptable_code:
        # 属于你,而且存在
        return _container_details_(
            container_name, client, port_start, ip_start
        )

    if belongs_to != username and status_code is None:
        # 不属于你，而且也不存在
        pass
    elif belongs_to != username and status_code in acceptable_code:
        # 不属于你，但是存在
        pass
    elif belongs_to != username and status_code not in acceptable_code:
        # 不属于你，但是存在
        pass
    # log status_code belongs_to username
    raise LabContainerStateException(
        container_name,status_code, belongs_to, username, 'detail'
    )

def _container_details_(container_name, client, port_start=6100, ip_start='10.18.242.2/24'):
    from collections import OrderedDict
    details = OrderedDict([
                        ('name',[]),
                        ('status',[]),
                        ('hostname',[]),
                        ('ipv4',[]),
                        ('create_at',[]),
                        ('port',[])
                        ])
    try:
        container = client.containers.get(container_name)
    except pylxd.exceptions.NotFound :
        details['name'].append(container_name)
        details['status'].append('not-exist')
        details['hostname'].append('not-exist')
        details['ipv4'].append('not-exist')
        details['create_at'].append('not-exist')
        details['port'].append(None)
    else:
        details['name'].append(container.name)
        details['status'].append(container.status)
        try:
            details['hostname'].append(container.state().network['eth0'].get('host_name', None))
        except (TypeError, KeyError) :
            # if container is stopped (will raise TypeError when ['eth0'])
            # if container has no eth0 it will raise KeyError
            details['hostname'].append(None)
        try:
            details['ipv4'].append(
                (
                    [i.get('address', None) for i in container.state().network['eth0']['addresses'] \
                        if (i['family']=='inet') and (i['scope']=='global')] \
                    or [None]
                )[0]
            )
        except:
            details['ipv4'].append(None)
        finally:
            details['port'].append(
                _iptables_port(
                    details['ipv4'][-1],
                    port_start=port_start,
                    ip_start=ip_start
                )
            )
            details['create_at'].append(container.created_at)
    return details
