#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, cgi
import simplejson as json
from optparse import OptionParser

from MuMuMasterLib.globals import *
from MuMuMasterLib.MuMuMaster import MuMuMaster
from MuMuMasterLib.SshHostHandler import SshHostHandler
from MuMuMasterLib.MuMuTuner import MuMuTuner
from MuMuMasterLib.RenderUI import RenderCLI, RenderCGI, RenderM3U


if __name__ == "__main__":
    # parser = OptionParser(description="list dvb")
    # parser.add_option('-f', '--format', action="store", dest="format", help="display format in 'cli','cgi,'m3u' [default:%default]", default='cli')
    # parser.add_option('-b', '--bouquet', action="store", dest="bouquet", help="filter, not yet implemented [default:%default]", default='all')
    # parser.add_option('-p', '--pretune', action="store_true", dest="pretune", help="if bouquet == single station, pretune here", default=False)
    #
    #
    # options, args = parser.parse_args()
    # cgi_data = cgi.FieldStorage()
    #
    # out_format = cgi_data.getvalue('format') or options.format
    # out_bouquet = cgi_data.getvalue('bouquet') or options.bouquet
    # out_pretune = cgi_data.getvalue('pretune') or options.pretune
    #
    # out_format = out_format.lower()
    # if out_format not in ['cli','cgi','m3u']:
    #     raise(Exception('unknown out_format ' + str(out_format)))


    import time
    stime = time.time()
    MyMuMuMasterInstance = MuMuMaster()


    MyUi = RenderCGI()

    # MyUi.title('configuration')

    for t in MyMuMuMasterInstance.tuners:
        assert isinstance(t, MuMuTuner)
        print '<h1>Current Tuner</h1>'
        print '<table style="width:100%", border=1>'
        for k,v in t.__dict__.iteritems():
            if isinstance(v, SshHostHandler):
                v = v.user + '@' + v.host + ':' + str(v.port)
            if str(v).startswith('http'):
                v = '<a href="' + v + '">' + v + '</a>'
            print '<tr>',
            print '<td>' + k + '</b>','<td>' + str(v) + '</td>'
            print '<td></td>'
            print '</tr>'

	print '<tr><td>get_state()</td> <td>'+str(t.get_status())+'</td><td></td></tr>'
        for k,v in t.get_current_config().iteritems():
            print '<tr><td>get_current_config()</td>',
            print '<td>' + k + '</b>','<td>' + str(v) + '</td>'
            print '</tr>'


    MyUi.table_end()

    for file in glob('config/*.json'):
        print '<h1>file ' + file + '</h1>'
        print "<pre>"
        print open(file,'r').read()
        print "</pre>"

    # MyUi.table_begin()
    # for s in list:
    #     assert isinstance(s, MuMuStation)
    #     MyUi.table_entry(s)
    # MyUi.table_end()
    # MyLogger.info("DONE, listed '" + out_bouquet + "' in " + str(round(time.time() - stime, 1)) + " secs")
