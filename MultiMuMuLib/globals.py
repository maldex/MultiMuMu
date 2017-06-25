# -*- coding: utf-8 -*-

import os, sys, logging, time, paramiko
reload(sys)
sys.setdefaultencoding('utf-8')

# logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='AutoMumu.log', level=logging.DEBUG)
# MyLogger = logging.getLogger('simple crap')
# MyLogger.setLevel( logging.DEBUG)

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='MultiMuMu.log', level=logging.DEBUG)
MyLogger = logging.getLogger('mumulib')
MyLogger.setLevel(logging.DEBUG)

logging.getLogger("paramiko").setLevel(logging.WARNING)

from glob import glob