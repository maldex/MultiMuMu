# -*- coding: utf-8 -*-
from .globals import *

class SshHostHandler(object):
    def __init__(self, server, username, password=None, port=22):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # try:    self.connection.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        # except: pass
        # try:    self.connection.load_system_host_keys()
        # except: pass
        self.connection.connect(server, port=port, username=username, password=password)
        self.host = server
        self.user = username
        self.port = port
        self.passwd = password

    def execute(self, cmd):
        (stdin, stdout, stderr) = self.connection.exec_command(cmd)
        err = stderr.read()
        if err != '':
            print((Exception("error while SSHing " + err)))
            return []
        return stdout.read().strip().split(os.linesep)

    def get_sftp(self):
        r = self.connection.open_sftp()
        assert isinstance(r, paramiko.SFTPClient)
        return r

    def get_dvb_tuners(self):
        r = []
        for t in self.execute('ls /dev/dvb/adapter*/frontend*'):
            adapter = t.split('/')[-2][7:]
            frontend = t.split('/')[-1][8:]
            if int(adapter) < 10: adapter = '0' + adapter
            if int(frontend) < 10: frontend = '0' + frontend
            r.append(adapter + frontend)
        return r

    def get_pids(self, process='mumudvb', filter=None):
        r = []
        for p in self.execute('ps -o pid,command -u ${USER}'):
            p = p.strip()
            pid = p.split(' ')[0]
            command = ' '.join(p.split(' ')[1:])
            if not command.startswith(process):
                continue
            if filter is not None and p.find(filter) < 0:
                continue
            r.append(pid)
        return r

    def kill_pid(self, pid, timeout=3):
        if pid == -1: return
        MyLogger.debug(self.host + ': stopping process ' + str(pid) )
        self.execute('kill -15 ' + str(pid))
        for c in range(0,timeout * 3):
            if pid not in self.execute('ps -o pid -u ${USER}'):
                return
            time.sleep(0.33)
        self.execute('kill -9 ' + pid)
        MyLogger.debug(self.host + ': pid ' + pid + ' had to be killed, terminating was not enough')
