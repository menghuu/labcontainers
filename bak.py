
def _containers_details2(containers_name, username, conn, client, port_start=61000, ip_start='10.18.242.2/24', encoding='utf-8'):
    '''use he subprocess.run to get the details, format is more beautiful,
    but cannot get the port information or cannot format the port infromation'''
    if not isinstance(containers_name, collections.Iterable):
        containers_name = [containers_name]
    if username is None:
        raise ValueError('username should not None')
    p1 = subprocess.run(['lxc', 'list'], stdout=subprocess.PIPE)
    headers = [header.decode(encoding) for header in p1.stdout.split(b'\n')[:3]]
    search_content = b'\n'.join(p1.stdout.split(b'\n')[3:])

    belongs = [_container_state(container_name, conn, client)[0]\
                for container_name in containers_name]
    flags = [1 if username == belong else 0 for belong in belongs]
    search_containers_name = [containers_name[i] for i in range(len(flags)) if flags[i]==1]
    sed_patterns = ['/| {} *|/p'.format(container_name) \
            for container_name in search_containers_name]

    sed_results = [subprocess.run(['sed', '-n', sed_pattern], \
            input=search_content, stdout=subprocess.PIPE).stdout\
            for sed_pattern in sed_patterns]
    sed_results = [sed_result.decode(encoding) for sed_result \
            in sed_results if sed_result is not None]
    result = '\n'.join(headers) + '\n' + \
            (( '-'*(len(headers[0])) ) + '\n').join(sed_results) +\
            '-'*len(headers[0])+'\n'
    return result
def _delete_spare(it):
    from collections import Iterable
    if isinstance(it, Iterable):
        if len(it) == 1:
            return it[0]
        else:
            return type(it)([_delete_spare(i) for i in it])
    else:
        return it

class LabUser(object):
    @property
    def owning_containers_name(self):
        return _owning_containers_name(self._name, self._conn)

    def is_mine(self, containers_name):
        if isinstance(containers_name, collections.Iterable):
            pass
        else:
            containers_name = [containers_name]
        return [True if container_name in self.owning_containers_name\
                else False for container_name in containers_name]
    @property
    def name(self):
        return self._name

    def __init__(self, name, db_path, lxc_client):
        self._name = name
        if isinstance(db_path, sqlite3.Connection):
            self._conn = db_path
        else:
            self._conn = sqlite3.connect(db_path)
        self._client = lxc_client

    def create_container(self, container_name, base_image_fingerprint, profiles=None):
        return _create_container(container_name, self._name, self._conn, self._client, base_image_fingerprint, profiles)

    def delete_container(self, container_name, enforce):
        return _delete_container(container_name, self._name, self._conn, \
                self._client, enforce)

    def start_container(self, container_name):
        return _start_container(container_name, self._name, self._conn, self._client)

    def stop_container(self, container_name):
        return _stop_container(container_name, self._name, self._conn, self._client)

    def launch_container(self, container_name, base_image_fingerprint):
        return _launch_container(container_name, self._name, self._conn,\
                self._client, base_image_fingerprint)

    def restart_container(self, container_name):
        return _restart_container(container_name, self._name, self._conn, self._client)

    def change_key(self, container_name, private_key=''):
        belongs_to, stauts_code = _container_state(container_name, self._conn, client)
        if belongs_to == self._name:
            if stauts_code in [103]:
                keys =_change_container_key(container_name, self._name, \
                        self._conn, self._client, private_key)
                return keys
        return None
