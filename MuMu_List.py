#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, cgi
import simplejson as json
from optparse import OptionParser

from MultiMuMuLib.globals import *
from MultiMuMuLib.MuMuStation import MuMuStation
from MultiMuMuLib.MuMuMaster import MuMuMaster
from MultiMuMuLib.RenderUI import RenderCLI, RenderCGI, RenderM3U


if __name__ == "__main__":
    MyLogger_log_http_source()
    parser = OptionParser(description="list dvb")
    parser.add_option('-f', '--format', action="store", dest="format", help="display format in 'cli','cgi,'m3u' [default:%default]", default='cli')
    parser.add_option('-b', '--bouquet', action="store", dest="bouquet", help="filter, not yet implemented [default:%default]", default='all')
    parser.add_option('-p', '--pretune', action="store_true", dest="pretune", help="if bouquet == single station, pretune here", default=False)


    options, args = parser.parse_args()
    cgi_data = cgi.FieldStorage()

    out_format = cgi_data.getvalue('format') or options.format
    out_bouquet = cgi_data.getvalue('bouquet') or options.bouquet
    out_pretune = cgi_data.getvalue('pretune') or options.pretune

    out_format = out_format.lower()
    if out_format not in ['cli','cgi','m3u']:
        raise(Exception('unknown out_format ' + str(out_format)))

    # initialize the right output render class
    if out_format == 'm3u':
        MyUi = RenderM3U()
    elif out_format == 'cgi' or os.environ.has_key('HTTP_USER_AGENT'):
        MyUi = RenderCGI()
    else:
        MyUi = RenderCLI()

    import time
    stime = time.time()
    MyLogger.info("listing " + out_bouquet)
    MyMuMuMasterInstance = MuMuMaster()


    MyUi.title('List of stations (' + out_bouquet + ')')

    list = []
    preTune = None

    favorites_file = 'config/favorite.' + out_bouquet + '.json'

    # types of list
    if out_bouquet == 'current':
        list = MyMuMuMasterInstance.get_current_stations()
    elif out_bouquet == 'all':
        list = MyMuMuMasterInstance.stations

    elif os.path.isfile(favorites_file):
        try:
            fc = open(favorites_file).read()
            favorites = json.loads(fc)
            for f in favorites:
                s = MyMuMuMasterInstance.get_station_by_name(f)
                if isinstance(s, MuMuStation):
                    list.append( s )
                else:
                    MyLogger.warn("unknown station '" + f + "' in " + favorites_file)
        except json.scanner.JSONDecodeError, e:
            MyLogger.error('could not decode ' + favorites_file)



    else:
        search = MyMuMuMasterInstance.get_station_by_name(out_bouquet)
        if search is None:
            MyLogger.critical("COULD NOT FIND '" + out_bouquet + "'")
            MyLogger.critical("mybe missing '" + favorites_file + "' ?")
            quit()
        list = [search]
        preTune = search


    MyUi.table_begin(['m3u','direct','proxy','host/tuner','freq','pol','srate','DiSEqC'])
    for s in list:
        assert isinstance(s, MuMuStation)
        MyUi.table_entry(s)
    MyUi.table_end()
    MyLogger.info("DONE, listed '" + out_bouquet + "' in " + str(round(time.time() - stime, 1)) + " secs")

    print
    if preTune is not None and out_pretune:
        assert isinstance(preTune, MuMuStation)
        MyLogger.info('m3u and direct station: assuming pre-tune')
        r = MyMuMuMasterInstance.tune_to(preTune)
        MyLogger.ddebug('m3u and direct station: pre-tuned ' + str(r))
        MyLogger.info("DONE, pretuned '" + out_bouquet + "' in " + str(round(time.time() - stime, 1)) + " secs")


