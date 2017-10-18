import sqlite3
import unittest

import pylxd
import pytest

from labuser import LabUser
from utils import _merge_details, _print_details


class LabUserTest(unittest.TestCase):
    def _gen_name(self, name):
        import random
        import uuid
        if name.startswith('testing'):
            return name + ''.join(random.sample(uuid.uuid1().hex, 4))
        else:
            return 'testing' + name + ''.join(random.sample(uuid.uuid1().hex, 4))
    def setUp(self):
        self.client = pylxd.Client()
        self.fingerprint = self.client.images.all()[0].fingerprint
        self.db_path = './lab.db'
        self.port_start = 61000
        self.ip_start = '10.18.242.2/24'
        self.conn = sqlite3.connect(':memory:')
        cursor = self.conn.cursor()
        cursor.execute(
            'CREATE TABLE lab_users'+\
            '(uid INTEGER PRIMARY KEY AUTOINCREMENT,'+\
                'username TEXT NOT NULL UNIQUE,'+\
                'password TEXT NOT NULL );'
            )
        cursor.execute(
                'CREATE TABLE lab_containers(\
                    container_name TEXT NOT NULL PRIMARY KEY UNIQUE,\
                    belongs_to_username TEXT NOT NULL,\
                    FOREIGN KEY(belongs_to_username) REFERENCES \
                        lab_users(username)\
                    );')
        cursor.close()
        self.conn.commit()
        self.username = self._gen_name('testing-user')
        self.user = LabUser(
            self.username, self.conn, self.client, 61000, '10.18.242.2/24'
        )

    def test_all(self):
        # create
        container_name = self._gen_name('testing-all')
        self.user.create_container(
           container_name, self.fingerprint
        )
        username2 = self._gen_name('testing-user2')
        user2 = LabUser(
            username2, self.db_path, self.client,
            self.port_start, self.ip_start
        )

        # if the container is exist, it will fail
        assert user2.create_container(
            container_name, self.fingerprint
        ) == 0

        print(
            self.user.container_details(container_name)
        )

        self.user.start_container(container_name)
        print(
            self.user.container_details(container_name)
        )
        _print_details(self.user.container_details(container_name))

        print('user add container, will test containers_details')
        container_name2 = self._gen_name('testing-container2')
        self.user.create_container(
            container_name2,
            self.fingerprint
        )

        _print_details(
            self.user.containers_details(
                self.user.owning_containers_name + user2.owning_containers_name
            )
        )

        # add not belong to
        user2.create_container(
            username2, self.fingerprint
        )
        _print_details(self.user.containers_details(user2.owning_containers_name))

        print(user2.container_details('not-found'))

        #

        _print_details(
            self.user.containers_details(
                self.user.owning_containers_name + user2.owning_containers_name
            )
        )

        # own it, should success, will print keys
        print(
            self.user.change_key(container_name)
        )

        # not own it, should fail, will print None
        print(
            self.user.change_key(container_name2)
        )

    def tearDown(self):
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
