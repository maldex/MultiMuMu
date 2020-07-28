#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, cgi
from optparse import OptionParser

from MultiMuMuLib.globals import *
from MultiMuMuLib.MuMuMaster import MuMuMaster


if __name__ == "__main__":
    MyLogger_log_http_source()
    parser = OptionParser(description="tune dvb")
    parser.add_option('-s', '--station', action="store", dest="station", help="station to tune to [default:%default]", default='prosieben austria')
    parser.add_option('-p', '--proxy', action="store_true", dest="proxy", help="forward to proxy instead of mumudvb direc", default=False)

    options, args = parser.parse_args()
    cgi_data = cgi.FieldStorage()

    station = cgi_data.getvalue('station') or options.station
    proxy = options.proxy
    if 'proxy' in cgi_data:
        proxy = cgi_data.getvalue('proxy').lower() == 'true'
    MyLogger.info("tuning to '" + station + "'     (Proxy:" + str( proxy  ) + ")")

    import time
    stime = time.time()

    MyMuMuMasterInstance = MuMuMaster()

    print(MyMuMuMasterInstance.tune_to(station, proxy=proxy))

    MyLogger.info("DONE, stream-up of '" + station + "' in total " + str(round(time.time() - stime, 1)) + " secs")
