import cmd
import getpass
import sqlite3

import pylxd

import lab_exceptions
from labuser import LabUser
from utils import _check_login, _images_detail, _print_details


class Prompt(cmd.Cmd, object):
    def __init__(self, db_path, lxc_client, port_start, ip_start,default_fingerprint, nobody='nobody'):
        super(Prompt, self).__init__()
        self._nobody = nobody or 'nobody'
        self._user = LabUser(self._nobody, db_path, lxc_client, port_start, ip_start)
        self.prompt = self._user.name+ '@gpu-server > '
        self.intro = 'welcome to haitaozhao\'s lab gpu server\nyou should login and do something on your lxc containers\n`help command` will show how to use the command `command`'
        if isinstance(db_path, sqlite3.Connection):
            self._conn = db_path
        else:
            self._conn = sqlite3.connect(db_path)
        self._client = lxc_client
        self._port_start = port_start
        self._ip_start = ip_start
        self._default_fingerprint=default_fingerprint
    def do_login(self, args):
        """login
            example:
                    login
                    # input your username and password
        """
        username = input('please input your username: ').strip()
        password = getpass.getpass('please input you password: ')
        if _check_login(username, password, self._conn):
            self._user = LabUser(username, self._conn, self._client, self._port_start, self._ip_start)
            print('login as username: {}'.format(self._user.name))
            self.prompt = self._user.name+ "@" + self.prompt.split('@')[1]
        else:
            print('wrong password with the username ', username)
    def do_logout(self, args):
        """logout
            example:
                    logout
        """
        self._user = LabUser(self._nobody, self._conn, self._client, self._port_start, self._ip_start)
        self.prompt = self._user.name + "@" + self.prompt.split('@')[1]
    def do_exit(self, args):
        """exit the termianl
            example:
                exit
        """
        return True
    def do_quit(self, args):
        """quit the termianl
            example:
                quit 
        """
        return self.do_exit(args)
    def do_details(self, args):
        """show the container details
            example:
                    details
        """
        if not args:
            containers_name = self._user.owning_containers_name
        else:
            args = args.split()
            containers_name = [container_name for container_name in args\
                if container_name in self._user.owning_containers_name]
        details = self._user.containers_details(containers_name)
        _print_details(details)
        #print(_containers_details2(containers_name, self._user.name, self._conn,\
        #        self._client))
    def do_detail(self, args):
        """show the container details
            example:
                    detail
        """
        self.do_details(args)
    def do_create(self, args):
        '''create the container if it is not exist, if exist will just drop this command 
            example: 
                    create `container-name`
                    create `container-name` -f `image-fingerprint`
            note:
                    `container-name` should not contain the `_`, you can get `image-fingerprint` with the command `images`
        '''
        if self._user.name == self._nobody:
            print('nobody cannot create container')
            return
        args = args.split()
        try:
            position = args.index('-f')
        except ValueError:
            position = -1
        if position >= 0 and position < len(args):
            tmp = args.copy()
            fingerprint = args[position+1]
            tmp.pop(position)
            tmp.pop(position)
            containers_name = tmp
        else:
            containers_name = args
            fingerprint = self._default_fingerprint
        container_name = containers_name[0]
        try:
            if self._user.create_container(container_name , fingerprint) == 1:
                print('create: success')
            else:
                print('not success, you may not own this container : ', container_name)
        except pylxd.exceptions.LXDAPIException as e:
            print('create: not success, the container\'s name is: {}, \nthe error information is: {}'.format(container_name, e))
    def do_delete(self, args):
        '''delete the container if it is not exist, if it does not exist or it does not belong to you, will fail 
            example: 
                    # will delete it when it is not running else will fail
                    delete `container-name`
                    # delete it, even it is running `-f` means `force`
                    create `container-name` -f 
        '''
        if args == '':
            print('at least one container name should be input')
            return
        args = args.split()
        try:
            position = args.index('-f')
        except ValueError:
            position = -1
        if position >= 0 :
            tmp = args.copy()
            tmp.pop(position)
            containers_name = tmp
            enforce = True
        else:
            containers_name = args
            enforce = False
        for container_name in containers_name:
            if self._user.delete_container(container_name, enforce) == 1:
                print('delete: success')
            else:
                print('delete: not success, you may not own this container({})) or it is running(you can use the flag `-f` to *force* delete the container)'.format(container_name))
    def do_start(self, args):
        '''start the container
            example: 
                    start `container-name`
        '''
        if args == '':
            print('at least one container name should be input')
        args = args.split()
        containers_name = args
        for container_name in containers_name:
            try:
                if self._user.start_container(container_name) == 1:
                    print('start: success')
                else:
                    print('start: not success,  you may not own this container({})'.format(container_name))
            except pylxd.exceptions.LXDAPIException as e:
                print('start: not success, the container\'s name is: {}, \nthe error information is: {}'.format(container_name, e))

    def do_stop(self, args):
        """stop the container
            example:
                    stop `container-name`
        """ 
        if args == '':
            print('at least one container name should be input')
            return
        args = args.split()
        containers_name = args
        for container_name in containers_name:
            try:
                if self._user.stop_container(container_name) == 1:
                    print('stop: success')
                else:
                    print('stop: not success, you may not own this container({})'\
                            .format(container_name))
            except pylxd.exceptions.LXDAPIException as e:
                print('stop: not success, the container\'s name is: {}, \nthe error information is: {}'.format(container_name, e))


    def do_launch(self, args):
        '''launch (create and start) the container if it is not exist, if exist will just start
            example: 
                    launch `container-name`
                    launch `container-name` -f `image-fingerprint`
            note:
                    `container-name` should not contain the `_`, you can get `image-fingerprint` with the command `images`
        '''
        if self._user.name == self._nobody:
            print('nobody cannot create container')
            return
        if args == '':
            print('at least one container name should be input')
            return
        args = args.split()
        try:
            position = args.index('-f')
        except ValueError:
            position = -1
        if position >= 0 and position < len(args):
            tmp = args.copy()
            fingerprint = args[position+1]
            tmp.pop(position)
            tmp.pop(position)
            containers_name = tmp
        else:
            containers_name = args
            fingerprint = self._default_fingerprint
        container_name = containers_name[0]
        try:
            if self._user.launch_container(container_name, fingerprint) == 1:
                print('launch: success')
            else:
                print('launch: not success, container name is {}'.format(container_name))
        except pylxd.exceptions.LXDAPIException as e:
            print('launch: not success, the container\'s name is: {}, \nthe error information is: {}'.format(container_name, e))

    def do_restart(self, args):
        """restart the container
            example:
                    restart `container-name`
        """
        if args == '':
            print('at least one container name should be input')
            return
        args = args.split()
        containers_name = args
        for container_name in containers_name:
            try:
                if self._user.restart_container(container_name) == 1:
                    print('restart: success')
                else:
                    print('restart: not success, container name is {}'.format(container_name))
            except pylxd.exceptions.LXDAPIException as e:
                print('restart: not success, the container\'s name is: {}, \nthe error information is: {}'.format(container_name, e))

    def do_key(self, args):
        """change the container public key
            example:
                    key `container-name`
            note:
                    it will generate a new paire of public key and private key, you can reuse this keys if you need
                    or, you can use those keys one time, the following are details: 
                    open another termianl, and copy the private key into `$HOME/.ssh/id_rsa` on you local machine if you are in linux or mac, 
                    then, you must change the file umask to 600,with the command `chmod 600 $HOME/.ssh/id_rsa`, 
                    if you have the file `id_rsa` already, do not delete it, just change another file name.
                    then you can login your gpu server with the command 
                    `ssh ubuntu@ip_of_real_remote_machine -p PORT -i $HOME/.ssh/id_rsa` or other file
                    you can get the `PORT` when you type `details` in current terminal, 
                    but the `ip_of_real_remote_machine` is not the ip in command `details`'s output, the ``ip_of_real_remote_machine` is your current termianl ip
                    if you already have a paire of private key and public key, you should know what you can do next,
                    simply: copy the public key into remote lxc container, and ssh into this lxc container with your private key
                    if you do not want use the public/private key to ssh into the container, 
                    you can config the remote lxc container `/etc/ssh/sshd_config` and login into lxc container with the user `ubuntu` password on remote lxc container
        """
        if args == '':
            print('at least one container name should be input')
            return
        args = args.split()
        try:
            position = args.index('-p')
        except ValueError:
            position = -1
        if position >= 0 and position < len(args):
            tmp = args.copy()
            private_key = args[position+1]
            tmp.pop(position)
            tmp.pop(position)
            containers_name = tmp
        else:
            containers_name = args
        container_name = containers_name[0]
        try:
            keys = self._user.change_key(container_name, private_key='')
            print('public key: (copy this to remote machine "/home/$USER/.ssh/authorized_keys")')
            print(keys['public_key'])
            print('private key: (copy this to local machine "/home/$USER/.ssh/id.rsa", make sure the file umask is 600 with the command `chmod 600 id.rsa`)')
            print(keys['private_key'])
        except pylxd.exceptions.LXDAPIException as e:
            print('key: not success, the container\'s name is: {}, \nthe error information is: {}'.format(container_name, e))

    def do_images(self, args):
        '''show the image details
            example:
                    images
        '''
        args = args.split()
        _print_details(_images_detail(self._client))
    def do_image(self, args):
        """show the image details
            example:
                    image
        """
        self.do_images(args)
