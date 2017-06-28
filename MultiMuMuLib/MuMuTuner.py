# -*- coding: utf-8 -*-
import os, sys, time, xmltodict, urllib2
from globals import *
from SshHostHandler import SshHostHandler

class MuMuTuner(object):
    STATUS_NA           =   1  # no process at all
    STATUS_STARTING     =   2  # mumudvb started, http interface not ready yet
    STATUS_AUTOCONFIG   =   3  # mumudvb started and serving some
    STATUS_SERVING      =   4  # mumudvb fully ready
    _TUNE_TIMEOUT       =   5
    def __init__(self, host, user=None, password=None, port=22, tuner='0000', http_port = 8500, http_prefix=None):
        self.tuner = tuner
        if user is None:
            user = os.environ['USER']
        self.ssh = SshHostHandler(host, user, password=password, port=port)
        if tuner not in self.ssh.get_dvb_tuners():
            MyLogger.error(self.ssh.host + ': tuner ' + tuner + ' not available!')
        self.http_port = http_port
        self.conffile = '/tmp/mumu-' + host + '-' + tuner + '.conf'
        self._http_conf = 'http://' + self.ssh.host + ':' + str(self.http_port)
        if http_prefix is not None:
            self._http_prefix = http_prefix
        else:
            self._http_prefix = self._http_conf

    def _get_my_pid(self):
        try:
            return self.ssh.get_pids('mumudvb', filter=self.conffile)[0]
        except IndexError:
            return -1       # no pid found

    def start(self, check_for_sid=None):
        if self.get_status() not in [self.STATUS_SERVING, self.STATUS_NA, self.STATUS_AUTOCONFIG]:
            MyLogger.warn(self.ssh.host + ': state is neither SERVING nor NA nor AUTOCONFIG, aborting')
            return False
        self.ssh.kill_pid(self._get_my_pid())

        cmd = "nohup mumudvb -d -c " + self.conffile + " > /tmp/mumuout-" + self.tuner + ".txt 2>&1 &"
        MyLogger.debug(self.ssh.host + ': running: ' + cmd)
        self.ssh.execute(cmd)

        stime = time.time()
        while self.get_status() not in [self.STATUS_SERVING, self.STATUS_NA, self.STATUS_AUTOCONFIG]:
            time.sleep(0.25)
            if time.time() - stime > self._TUNE_TIMEOUT:
                MyLogger.error( self.ssh.host + ': mumudvb exceeded time to start, aborting')
                self.ssh.kill_pid(self._get_my_pid())
                return False

        if isinstance(check_for_sid, int):  # number
            stime2 = time.time()
            MyLogger.debug('waiting for sid ' + str(check_for_sid) + ' to appear')
            while ( time.time() - stime2 < self._TUNE_TIMEOUT ) or ( check_for_sid not in self.get_current_config()['sids']):
                time.sleep(0.25)
            MyLogger.info(self.ssh.host + ': ' + self.tuner + ' found sid '+ str(check_for_sid) + ' in ' + str(round(time.time() - stime2, 1)) + ' secs.')

        MyLogger.info(self.ssh.host + ': ' + self.tuner + ' tuned in ' + str(round(time.time() - stime, 1)) + ' secs. pid: ' + str(self._get_my_pid()) + ' ' + self._http_conf)

        return  self.get_status() != self.STATUS_NA

    def set_config(self, freq=562000, pol=None, srate=None, diseqc=None, sids=[], comment_list=['blalba']):
        r = ['# auto generated ... will be overwritten soon']
        r += ['card=' + str(int(self.tuner[:2]))]
        r += ['tuner=' + str(int(self.tuner[2:]))]
        r += ['port_http=' + str(self.http_port), 'ip_http=0.0.0.0']
        r += ['']
        r += ['#multicast=0','multicast_ipv4=0','unicast=1']
        r += ['sort_eit=1','autoconfiguration=full', 'autoconf_name_template=%name']
        r += ['']
        r += ['freq=' + str(freq) ]
        if pol is not None:
            r += ['pol=' + pol]
        if srate is not None:
            r += ['srate=' + str(srate)]
        if diseqc is not None:
            r += ['sat_number=' + str(diseqc)]
        r += ['autoconf_sid_list=' + ' '.join(str(x) for x in sids) ]
        r += ['']
        r += (str('# '+ x) for x in comment_list)
        r += ['']

        MyLogger.debug(self.ssh.host + ': saving new mumuconfig: ' + self.conffile)

        with self.ssh.get_sftp() as sftp:
            with sftp.open(self.conffile,'w') as f:
                f.write(os.linesep.join(r))
        return r



    def get_status(self):
        if self._get_my_pid() == -1:
            return self.STATUS_NA
        try:
            response = urllib2.urlopen(self._http_conf + '/monitor/state.xml').read()
        except urllib2.URLError:   # internal http not ready yet
            return self.STATUS_STARTING
        except Exception:    # or socket.error
            return self.STATUS_NA

        self._status_data = xmltodict.parse(response)['mumudvb']
        if self._status_data['autoconfiguration_finished'] == '0':
            return self.STATUS_AUTOCONFIG  # autoconfig not done yet
        return self.STATUS_SERVING


    def get_current_config(self):
        cc = {}
        cc['sids'] = []
        if self.get_status() <= self.STATUS_STARTING:
            return cc

        cc['freq'] = float(self._status_data['frontend_frequency'])
        if self._status_data['frontend_system'] == 'DVB-S':
            cc['freq'] /= 1000
            cc['pol'] = self._status_data['frontend_polarization']
            cc['diseqc'] = int(self._status_data['frontend_satnumber'])/1000
            cc['srate'] = int(self._status_data['frontend_symbolrate'])/1000

        try:
            response = urllib2.urlopen(self._http_conf + '/playlist.m3u').read()
        except urllib2.URLError:   # internal http not ready yet
            return cc
        for l in response.split(os.linesep):
            if l.startswith('http://'):
                cc['sids'].append(int(l.split('/')[-1]))
        return cc
