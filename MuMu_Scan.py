#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import simplejson as json
from optparse import OptionParser

import xmltodict, os

from MultiMuMuLib.globals import *
from MultiMuMuLib.MuMuStation import MuMuStation
from MultiMuMuLib.MuMuTuner import MuMuTuner, SshHostHandler

############    ##########################################################################################

class StupidLogger(object):
    def _out(self,s):
        print s
    def error(self,s):
        self._out('ERROR:' + s)
    def warn(self, s):
        self._out('WARN:' + s)
    def info(self, s):
        self._out('INFO:' + s)
    def debug(self, s):
        self._out('DEBUG:' + s)

MyLogger_scan = StupidLogger()

class MuMuTunerScanner(SshHostHandler):

    def init(self, tuner, type):
        self.tuner = tuner
        self.type = type
        self.stations = []

    def w_scan(self, country=None, sat=None, DiSEqC=None):
        # w_scan -R0 -T1 -O0 -E0 -fs --diseqc-switch 2c -a /dev/dvb/adapter0 -s S19E2 -L
        outfile = '/tmp/scan.' + self.host + '.' + self.tuner + '.' + self.type + '.' + str(sat) + '.' + str(DiSEqC)
        adapter = 'adapter' + str(int(self.tuner[:2]))
        tuner = 'frontend' + str(int(self.tuner[2:]))
        cmd = "w_scan -R0 -T1 -O0 -E0 -f" + self.type
        if DiSEqC is not None:
            cmd += " --diseqc-switch " + str(DiSEqC) + "c"
        cmd += " -a /dev/dvb/" + adapter + "/" + tuner
        if country is not None:
            cmd += " --country " + country
        if sat is not None:
            cmd += " -s " + sat
        cmd += " --output-VLC"
        # cmd = "w_scan -fs -a /dev/dvb/adapter0/frontend1 --satellite S19E2 -R0 -T1 -O0 -E0 --diseqc-switch 0c --output-VLC"
        # cmd = "w_scan -R0 -T1 -O0 -E0 -fs --diseqc-switch 2c -a /dev/dvb/adapter0 -s S19E2 -L"   # works

        # cmd =   "w_scan -R0 -T1 -O0 -E0 -fs --diseqc-switch 0c -a /dev/dvb/adapter0/frontend1 --satellite S19E2 --output-VLC"
        cmd += " 2>" + outfile + ".out > " + outfile + ".xspf"

        return cmd, outfile + '.xspf'

    def scan_and_decode_xsfp_to_AM_station(self, country=None, sat=None, DiSEqC=None, do_scan=False):
        MyLogger_scan.info(self.host + ": scanning on tuner:" + self.tuner + " sat:"+str(sat) + " DiSEqC:" + str(DiSEqC) )

        cmd, outfile = self.w_scan(country=country, sat=sat, DiSEqC=DiSEqC)
        MyLogger_scan.debug(self.host + ": " + cmd)
        if do_scan:
            MyLogger_scan.info(self.host + ": scanning ... this will take a while")
            self.execute(cmd)
        else:
            MyLogger_scan.info(self.host + ": missing --do_scan, skipping the actual scan")

        MyLogger_scan.debug(self.host + ": fetching contents of " + outfile)

        try:
            self.execute('cp ' + outfile + ' ' + outfile + '.2')
            with self.get_sftp() as sftp:
                with sftp.open(outfile, 'r') as f:
                    scan_result_raw = f.read()
        except Exception, e:
            MyLogger_scan.error(str(e) + ': ' + outfile)
            return False

        try:
            doc = xmltodict.parse(scan_result_raw)
        except Exception, e:
            MyLogger_scan.error(str(e) + ': ' + outfile)
            return False

        try:  # trying to access keys within the document
            MyLogger_scan.info('found ' + str(len(doc['playlist']['trackList']['track'])) +' stations')
        except KeyError:
            MyLogger_scan.error('no playlist/trackList/track found!')
            return False
        except TypeError:
            MyLogger_scan.error('no playlist/trackList/track found!')
            return False


        for e in doc['playlist']['trackList']['track']:
            s_title = e['title'][6:].encode('utf-8')
            if s_title == '.' or s_title.startswith('service_id'):
                continue

            s_freq = float(e['location'].split('=')[1]) / 1000
            option = {}
            for v in e['extension']['vlc:option']:
                kv = v.split('=')
                option[kv[0]] = kv[1]
            # pprint(option)
            s_sid = int(option['program'])

            station = MuMuStation()
            station.init(s_title, s_sid, s_freq)

            if option.has_key('dvb-polarization'):
                station.dvbs_pol(option['dvb-polarization'])
            if option.has_key('dvb-satno'):
                station.dvbs_diseqc(int(option['dvb-satno']))
            if option.has_key('dvb-srate'):
                station.dvbs_srate(int(option['dvb-srate']) / 1000)

            self.stations.append(station)

        return True

    def do_it(self, do_scan=False):
        r = True
        if self.type == 't':
            r = (r and self.scan_and_decode_xsfp_to_AM_station( do_scan=do_scan))

        if self.type == 's':
            #for sat in ['S16E0','S20E0','S13E0']:
            for sat in ['S19E2', 'S13E0', 'S9E0', 'S10E0', 'S16E0', 'S20E0', 'S21E6']:
#            for sat in ['S13E0','S16E0','S19E2']:
                for diseqc in range(0, 4):
                    b = self.scan_and_decode_xsfp_to_AM_station(sat=sat, DiSEqC=diseqc, do_scan=do_scan)
                    r = (r and b)
                    self.save()
        self.save()
        return r

    def save(self):
        if len(self.stations) == 0:
            MyLogger_scan.warn('no stations so far found')
            return
        tuner_cfg = 'config/tuner.' + self.host + '-' + self.tuner + '.json'
        station_cfg = 'config/station.' + self.host + '-' + self.tuner + '.json'
        http_port =  8500 + int(self.tuner)
        tc = { 'ssh_user': self.user,
               'ssh_host': self.host,
               'ssh_port': self.port,
               'ssh_pass': self.passwd,
               'http_port': http_port,
               'http_prefix': 'http://' + self.host + ':' + str(http_port),
               'tuner': self.tuner,
               'station_cfg': station_cfg
        }
        with open(tuner_cfg, 'w') as f:
            f.write(json.dumps(tc, indent=4, sort_keys=True))
            MyLogger_scan.info('Wrote tuner-config to ' + tuner_cfg)

        with open(station_cfg, 'w') as f:
            f.write('[' + os.linesep)
            for s in self.stations[:-1]:
                f.write(s.serialize() + ',' + os.linesep)
            f.write(self.stations[-1].serialize() + os.linesep)
            f.write(']')
            MyLogger_scan.info('Wrote station-config to ' + tuner_cfg + '    (' + str(len(self.stations)) + ' stations)')






#######################################################################################################

if __name__ == "__main__":

    parser = OptionParser(description="remote scan for dvb")
    # parser.add_option('-c', action="store", dest="cfgfile", help="PassWebTool keepass config  [default:%default]",
    #                   default="config.json")
    # parser.add_option('-p', action="store", dest="kppass", help="KeePass: Password  [default:********]", default="PassWebTool")
    parser.add_option('-H', '--host', action="store", dest="host", help="SSH: hostname")
    parser.add_option('-U', '--user', action="store", dest="user", help="SSH: username [default:%default]", default=os.environ['USER'])
    parser.add_option('-P', '--pass', action="store", dest="passwd", help="SSH: password [default:%default]", default=None)
    parser.add_option('-p', '--port', action="store", dest="port", help="SSH: port [default:%default]", default=22)

    parser.add_option('-T', '--tuner', action="store", dest="tuner", help="tuner to scan. e.g 0103 = adapter1/frontend3 [default:%default]", default='0000')
    parser.add_option('-t', '--type', action="store", dest="type", help="dvb-type. e.g 't'err., 's'atellite, 'c'able [default:%default]", default='t')
    parser.add_option('-s', '--do_scan', action="store_true", dest="do_scan", help="actually do run w_scan, or just fetch output files")
    options, args = parser.parse_args()

    if not options.host :
        print "use -h"; quit(1)

#######################################################################################################

    MyLogger.info("SSH Connect to '" + options.user + "@" + options.host + ":" + str(options.port) + "'")
    MyScanner = MuMuTunerScanner(options.host, options.user, options.passwd, options.port)
    MyScanner.init(tuner=options.tuner, type=options.type)

    print MyScanner.do_it(options.do_scan)






















#
#     MyHost = AM_Host()
#     MyHost.init(options.host, options.user, options.passwd)
#     MyHost.connect()
#     logging.info("found the following tuners: " + str(MyHost.tuners.keys()))
#
#     for t in MyHost.tuners.keys():
#         sfile = options.host + '-' + t + '.json'
#         MyHost.tuners[t] = sfile
#
#         stations = []
#
#
#         if options.dvb == 't':
#             stations += scan_and_decode_xsfp_to_AM_station(tuner=t, country='CH', do_scan=options.do_scan)
#             # pprint(stations)
#
#         if options.dvb == 's':
#             for s in ['S19E2', 'S13E0']:
#                 for d in range(0,3):
#                     stations += scan_and_decode_xsfp_to_AM_station(tuner=t, type=options.dvb, country='CH', DiSEqC=d, sat=s, do_scan=options.do_scan)
#
#
#         with open(sfile,'w') as f:
#             for s in stations:
#                 # print s.serialize()
#                 f.write(s.serialize() + os.linesep)
#             logging.info('wrote ' + str(len(stations)) + ' stations into ' + sfile)
#
#
#         logging.info("writing hostinfo " + options.host + ".json")
#         with open(options.host + '.json', 'w') as f:
#             # print MyHost.serialize(hr=True)
#             f.write(MyHost.serialize(hr=True))
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# #     for t in adapters[a]:
# #         if options.dvb == 't':
# #             outfile = x.scan(adapter=a,tuner=t, country='CH', do_scan=False)
# #
# #         if options.dvb == 's':
# #                 for d in range(0,4):
# #                     outfile = x.scan(adapter=a, tuner=t, type=options.dvb, country='CH', DiSEqC=d, sat='S19E2', do_scan=False)
# #
# #         t_ident = '0'+a[7:]+'0'+t[8:] + '-raw'
# #         h.tuners[t_ident] = outfile + ".xspf"
# #
# #
# #         print "checkout:"
# #         print outfile + ".out   <- for scan results"
# #         print outfile + ".xspf  <- to be run into"
# #
# #
# # with open(options.host + '.json', 'w') as f:
# #     f.write(h.serialize())
# # print "./xspf_to_chanlist2.py -i " + options.host + ".json"
#
#
