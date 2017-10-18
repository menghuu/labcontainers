#!/usr/bin/env python3

import random
import sqlite3
import unittest
import uuid
import warnings
import pylxd
import pytest

from lab_exceptions import LabContainerStateException
from manager_lxc_utils import (_change_container_key, _container_details,
                               _create_container, _delete_container,
                               _launch_container, _restart_container,
                               _start_container, _stop_container,
                               _change_container_password)

class TestCreateContainer(unittest.TestCase):

    """test the most common container operators"""
    def _create_container_with_user(self, container_name, username, password='password'):
        cursor = self.conn.cursor()
        cursor.execute(
            'insert into lab_users(username, password) values (?,?);',
            (username, password)
        )
        self.conn.commit()
        _create_container(container_name, username, self.conn, self.client, self.fingerprint)
        cursor.close()
    @classmethod
    def setUpClass(self):
        warnings.simplefilter('ignore')
        self.client = pylxd.Client()
        self.fingerprint = self.client.images.all()[0].fingerprint
        self.conn = sqlite3.connect(':memory:')
        self.username = 'mongoose'
        self.password = 'password'
        cursor = self.conn.cursor()
        # create lab_users
        cursor.execute(
            'CREATE TABLE lab_users'+\
            '(uid INTEGER PRIMARY KEY AUTOINCREMENT,'+\
                'username TEXT NOT NULL UNIQUE,'+\
                'password TEXT NOT NULL );'
            )
        # insert one record into lab_users
        cursor.execute('insert into lab_users(username, password) values(?,?)', (self.username, \
                self.password))
        # create lab_containers
        cursor.execute(
                'CREATE TABLE lab_containers(\
                    container_name TEXT NOT NULL PRIMARY KEY UNIQUE,\
                    belongs_to_username TEXT NOT NULL,\
                    FOREIGN KEY(belongs_to_username) REFERENCES \
                        lab_users(username)\
                    );')
        cursor.close()
        self.conn.commit()

    def _gen_name(self, name):
        if name.startswith('testing'):
            return name + ''.join(random.sample(uuid.uuid1().hex, 4))
        else:
            return 'testing' + name + ''.join(random.sample(uuid.uuid1().hex, 4))
    def test_create_details(self):
        """测试创建时的细节"""
        username = self._gen_name('testing-create-details-user')
        password = 'password'
        container_name = self._gen_name('testing-with-split-line')
        cursor = self.conn.cursor()
        cursor.execute(
            'insert into lab_users(username, password) values(?,?);',
            (username, password)
        )
        self.conn.commit()
        _create_container(
            container_name, username,
            self.conn, self.client, self.fingerprint
        )

        # 测试下划线的容器名字是否能够创建成功，事实是会失败
        container_name2 = self._gen_name('testing_with_underline')
        self.assertRaisesRegex(
            pylxd.exceptions.LXDAPIException, 'Container name isn\'t a valid hostname.',
            _create_container,
            container_name2, username,
            self.conn, self.client, self.fingerprint
        )
        cursor.execute(
            'select * from lab_containers where container_name = ?;',
            (container_name2,)
        )
        self.assertIsNone(
            cursor.fetchone()
        )

        # 重复创建应该会直接返回，不会出错

        _create_container(container_name, username, self.conn, self.client, self.fingerprint)
    def test_change_container_password(self):
        username = self._gen_name('testing-user-change-password')
        password = 'password'
        container_name = 'testing-container-change-password'
        self._create_container_with_user(
            container_name, username
        )

        with pytest.raises(LabContainerStateException):
            _change_container_password(
                container_name, username,
                self.conn, self.client, 'ceshimima'
            )
        _start_container(
            container_name, username, self.conn, self.client
        )
        _change_container_password(
            container_name, username,
            self.conn, self.client, 'ceshimima'
        )


    @classmethod
    def tearDownClass(self):
        cursor = self.conn.cursor()
        cursor.execute('select username from lab_users;')
        usernames = [names[0] for names in cursor.fetchall() if names[0].startswith('testing') ]
        for username in usernames:
            cursor.execute('delete from lab_users where username=?;', (username,))
            cursor.execute('delete from lab_containers where belongs_to_username = ?;', (username,))
            cursor.execute('delete from lab_containers where container_name glob \'testing*\';')
        container_names = [
            c.name for c in self.client.containers.all() if c.name.startswith('testing')
        ]
        # print('container_names is ', container_names)
        for name in container_names:
            try:
                self.client.containers.get(name).stop(force=True, wait=True)
            except Exception as e:
                pass
            # print('will delete ', name)
            self.client.containers.get(name).delete()
            # print(name, ' is deleted')
        cursor.close()
        self.conn.close()

    def _exist_username_in_db(self, username):
        c = self.conn.cursor()
        c.execute(
            'select * from lab_users where username = ?',
            (username,)
        )
        if c.fetchone() is None:
            return False
        else:
            return True
    def _get_belongs_to_in_db(self, container_name):
        """默认认为在数据库中存在这个容器，但是有可能这个belongsto的这个人不在lab_containers表中"""
        c = self.conn.cursor()
        c.execute(
            'select belongs_to from lab_containers where container_name = ?',
            (container_name,)
        )
        return c.fetchone()[0]
    def _exist_container_in_lxc(self, container_name):
        try:
            self.client.containers.get(container_name)
        except pylxd.exceptions.NotFound:
            return False
        else:
            return True
    def _exist_container_in_db(self, container_name):
        c = self.conn.cursor()
        c.execute(
            'select * from lab_containers where container_name = ?;',
            (container_name,)
        )
        if c.fetchone() is None:
            return False
        else:
            return True
    def _get_container_status_code(self, container_name):
        return self.client.containers.get(container_name).status_code
    def test_all(self):
        username = self._gen_name('testing-all-user')
        container_name = self._gen_name('testing-all-container')
        password = 'password'

        cursor = self.conn.cursor()

        self.assertFalse(self._exist_username_in_db(username))

        cursor.execute(
            'insert into lab_users(username, password) values (?,?);',
            (username, password)
        )
        self.conn.commit()
        self.assertTrue(
            self._exist_username_in_db(username)
        )
        # 不存在container
        self.assertFalse(self._exist_container_in_lxc(container_name))

        # 创建容器
        _create_container(container_name, username, self.conn, self.client, self.fingerprint)
        self.assertTrue(
            self._exist_container_in_lxc(container_name)
        )
        self.assertTrue(
            self._exist_container_in_db(container_name)
        )
        self.assertEqual(
            self.client.containers.get(container_name).status_code,
            102
        )

        # test start
        _start_container(container_name, username, self.conn, self.client)
        self.assertEqual(
            self.client.containers.get(container_name).status_code,
            103
        )

        # test stop
        _stop_container(container_name, username, self.conn, self.client)
        self.assertEqual(
            self.client.containers.get(container_name).status_code,
            102
        )

        # test delete without force
        _delete_container(container_name, username, self.conn, self.client)
        self.assertFalse(
            self._exist_container_in_lxc(container_name)
        )
        self.assertFalse(
            self._exist_container_in_db(container_name)
        )

        # test laumch when the container does not exist
        _launch_container(container_name, username, self.conn, self.client, self.fingerprint)
        self.assertTrue(
            self._exist_container_in_lxc(container_name)
        )
        self.assertTrue(
            self._exist_container_in_db(container_name)
        )
        self.assertEqual(
            self.client.containers.get(container_name).status_code,
            103
        )

        # test launch when container does exist
        _stop_container(container_name, username, self.conn, self.client)
        _launch_container(container_name, username, self.conn, self.client, self.fingerprint)
        self.assertTrue(
            self._exist_container_in_lxc(container_name)
        )
        self.assertTrue(
            self._exist_container_in_db(container_name)
        )
        self.assertEqual(
            self.client.containers.get(container_name).status_code,
            103
        )

        # test restart when running
        _restart_container(container_name, username, self.conn, self.client)
        self.assertEqual(
            self.client.containers.get(container_name).status_code,
            103
        )

        # test restart when stop
        _stop_container(container_name, username, self.conn, self.client)
        _restart_container(container_name, username, self.conn, self.client)
        self.assertEqual(
            self.client.containers.get(container_name).status_code,
            103
        )

        print(_container_details(
            container_name, username, self.conn, self.client,
            port_start=61000, ip_start='10.18.242.2/24'
        ))

        # test delete with force
        _delete_container(container_name, username, self.conn, self.client, enforce=True)
        self.assertFalse(
            self._exist_container_in_db(container_name)
        )
        self.assertFalse(
            self._exist_container_in_lxc(container_name)
        )
        cursor.close()
    def test_details(self):
        username = self._gen_name('testing-user-details')
        container_name = self._gen_name('testing-container-details')
        self._create_container_with_user(container_name, username)
        print('the container is not running')
        print(_container_details(
            container_name, username, self.conn, self.client,
            port_start=61000, ip_start='10.18.242.2/24'
        ))
        _start_container(container_name, username, self.conn, self.client)
        print('the container is running')
        print(_container_details(
            container_name, username, self.conn, self.client,
            port_start=61000, ip_start='10.18.242.2/24'
        ))
        print('the container does not belong to the ', username+'-not-belong', ' will raise LabContainerStateException')
        self.assertRaises(
            LabContainerStateException,
            _container_details,
            container_name, username+'-not-belong', self.conn,
            self.client, port_start=61000, ip_start='10.18.242.2/24'
        )
    def test_change_key(self):
        username = self._gen_name('testing-user-change-key')
        container_name = self._gen_name('testing-container-change-key')
        self._create_container_with_user(container_name, username)
        print('if the container is not running, it will raise exception')
        self.assertRaises(
            LabContainerStateException,
            _change_container_key,
            container_name, username, self.conn, self.client, ''
        )
        _start_container(container_name, username, self.conn, self.client)
        print('will it put the key?')
        keys = _change_container_key(
            container_name, username, self.conn, self.client, ''
        )
        for k  in keys:
            print('{} is \n{}'.format(k, keys[k]))

        _stop_container(
            container_name, username, self.conn, self.client
        )

    def test_all_fail(self):
        username = self._gen_name('testing-all-fail-user')
        container_name = self._gen_name('testing-all-fail-container')
        password = 'password'

        cursor = self.conn.cursor()

        self.assertFalse(self._exist_username_in_db(username))

        cursor.execute(
            'insert into lab_users(username, password) values (?,?);',
            (username, password)
        )
        self.conn.commit()
        self.assertTrue(
            self._exist_username_in_db(username)
        )
        # 不存在container
        self.assertFalse(self._exist_container_in_lxc(container_name))

        with pytest.raises(LabContainerStateException):
            try:
                _stop_container(
                    container_name, username, self.conn, self.client
                )
            except LabContainerStateException as e:
                assert e.status_code is None
                raise e

        with pytest.raises(LabContainerStateException):
            try:
                _restart_container(
                    container_name, username, self.conn, self.client
                )
            except LabContainerStateException as e:
                assert e.status_code is None
                raise e

        with pytest.raises(LabContainerStateException):
            try:
                _delete_container(
                    container_name, username, self.conn, self.client
                )
            except LabContainerStateException as e:
                assert e.status_code is None
                raise e
