#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, cgi
from optparse import OptionParser

from MultiMuMuLib.globals import *
from MultiMuMuLib.MuMuMaster import MuMuMaster


if __name__ == "__main__":
    parser = OptionParser(description="tune dvb")
    parser.add_option('-s', '--station', action="store", dest="station", help="station to tune to [default:%default]", default='prosieben austria')

    options, args = parser.parse_args()
    cgi_data = cgi.FieldStorage()

    station = cgi_data.getvalue('station') or options.station
    MyLogger.info("tuning to '" + station + "'")

    import time
    stime = time.time()

    MyMuMuMasterInstance = MuMuMaster()

    print MyMuMuMasterInstance.tune_to(station)

    MyLogger.info("DONE, tuned to '" + station + "' in " + str(round(time.time() - stime, 1)) + " secs")
