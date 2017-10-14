import unittest
from utils import _check_login, _add_lab_user
import sqlite3
import pytest

class AdminTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        cursor = self.conn.cursor()
        # create lab_users
        cursor.execute(
            'CREATE TABLE lab_users'+\
            '(uid INTEGER PRIMARY KEY AUTOINCREMENT,'+\
                'username TEXT NOT NULL UNIQUE,'+\
                'password TEXT NOT NULL,'+\
                'salt TEXT NOT NULL);'
            )
        # insert one record into lab_users
        self.conn.commit()
    def test_add_user(self):
        cursor = self.conn.cursor()
        username = 'testing-add-user'
        password = 'testing-add-user'
        cursor.execute('select * from lab_users where username = ?;', (username,))
        self.assertIsNone(cursor.fetchone())

        self.assertFalse(_check_login(username, password, self.conn))
        # self.assertIsNotNone(result)
        self.assertTrue(_add_lab_user(username, password, self.conn))

        self.assertTrue(_check_login(username, password, self.conn))
        
