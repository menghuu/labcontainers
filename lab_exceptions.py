#!/usr/bin/env python3
import json


class LabException(Exception):
    def __init__(self):
        super(LabException, self).__init__()

# class ContainerStateException(LabContainerStateException, LabException, RuntimeError):
#     pass
class ContainerIPException(LabException, RuntimeError):
    pass
class LabContainerStateException(LabException, RuntimeError):

    """Exception because of state error"""

    def __init__(self, container_name, state, belongs_to, username, when=None):
        super(LabContainerStateException, self).__init__()
        self.container_name = container_name
        self.state = state
        self.status_code = state
        self.belongs_to = belongs_to
        self.username = username
        self.when = when

    def __str__(self):
        return super(LabContainerStateException, self).__str__() + \
        json.dumps(
            {
                'state':self.state,
                'belongs_to': self.belongs_to,
                'username': self.username,
                'when': self.when
            }
        )
