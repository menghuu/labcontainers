#!/usr/bin/env python3
import sqlite3

import lab_exceptions
from manager_lxc_utils import (_change_container_key, _container_details,
                               _create_container, _delete_container,
                               _launch_container, _restart_container,
                               _start_container, _stop_container)
from utils import _owning_containers_name


class LabUser(object):
    @property
    def owning_containers_name(self):
        return _owning_containers_name(self._name, self._conn)

    def is_mine(self, containers_name):
        import collections
        if isinstance(containers_name, collections.Iterable):
            pass
        else:
            containers_name = [containers_name]
        return [True if container_name in self.owning_containers_name\
                else False for container_name in containers_name]
    @property
    def name(self):
        return self._name

    def __init__(self, name, db_path, lxc_client, port_start, ip_start):
        self._name = name
        if isinstance(db_path, sqlite3.Connection):
            self._conn = db_path
        else:
            self._conn = sqlite3.connect(db_path)
        self._client = lxc_client
        self._port_start = port_start
        self._ip_start = ip_start

    def create_container(
        self, container_name, base_image_fingerprint, profiles=None):
        try:
            _create_container(
                container_name, self.name, self._conn,
                self._client, base_image_fingerprint,
                profiles=profiles
            )
            return 1
        except lab_exceptions.LabException:
            return 0

    def stop_container(self, container_name):
        try:
            _stop_container(
                container_name, self.name,
                self._conn, self._client
            )
            return 1
        except lab_exceptions.LabException:
            return 0

    def delete_container(self, container_name, enforce):
        try:
            _delete_container(
                container_name, self.name, self._conn,
                self._client, enforce=enforce
            )
            return 1
        except lab_exceptions.LabException:
            return 0

    def start_container(self, container_name):
        try:
            _start_container(
                container_name, self.name, self._conn, self._client
            )
            return 1
        except lab_exceptions.LabException:
            return 0

    def launch_container(self, container_name, base_image_fingerprint):
        try:
            _launch_container(
                container_name, self.name, self._conn, self._client,
                base_image_fingerprint
            )
            return 1
        except lab_exceptions.LabException:
            return 0

    def restart_container(self, container_name):
        try:
            _restart_container(
                container_name, self.name, self._conn, self._client
            )
            return 1
        except lab_exceptions.LabException:
            return 0

    def container_details(self, container_name):
        from collections import OrderedDict
        try:
            return _container_details(
            container_name, self.name, self._conn, self._client,
            self._port_start, self._ip_start
            )
        except lab_exceptions.LabContainerStateException as e:
            if e.status_code is None:
                return OrderedDict([
                        ('name',[container_name]),
                        ('status',['not exist']),
                        ('hostname',['not exist']),
                        ('ipv4',['not exist']),
                        ('create_at',['not exist']),
                        ('port',['not exist'])
                        ])
            if e.belongs_to != self.name:
                return OrderedDict([
                        ('name',[container_name]),
                        ('status',['not belong']),
                        ('hostname',['not belong']),
                        ('ipv4',['not belong']),
                        ('create_at',['not belong']),
                        ('port',['not exist'])
                        ])
    def containers_details(self, containers_name):
        import collections
        from collections import OrderedDict
        if isinstance(containers_name, collections.Iterable):
            containers_name = list(containers_name)
        else:
            containers_name = [containers_name]
        details = OrderedDict([
                    ('name',[]),
                    ('status',[]),
                    ('hostname',[]),
                    ('ipv4',[]),
                    ('create_at',[]),
                    ('port',[])
                    ])
        for container_name in containers_name:
            try:
                d = _container_details(
                container_name, self.name, self._conn, self._client,
                self._port_start, self._ip_start
                )
            except lab_exceptions.LabContainerStateException as e:
                if e.status_code is None:
                    d = OrderedDict([
                            ('name',[container_name]),
                            ('status',['not exist']),
                            ('hostname',['not exist']),
                            ('ipv4',['not exist']),
                            ('create_at',['not exist']),
                            ('port',['not exist'])
                            ])
                if e.belongs_to != self.name:
                    d = OrderedDict([
                            ('name',[container_name]),
                            ('status',['not belong']),
                            ('hostname',['not belong']),
                            ('ipv4',['not belong']),
                            ('create_at',['not belong']),
                            ('port',['not exist'])
                            ])
            for k in d:
                details[k] += d[k]
        return details

    def change_key(self, container_name, private_key=''):
        try:
            return _change_container_key(
            container_name, self.name, self._conn, self._client, private_key
            )
        except lab_exceptions.LabException:
            return None
