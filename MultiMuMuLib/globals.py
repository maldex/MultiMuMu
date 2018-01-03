# -*- coding: utf-8 -*-

import os, sys, logging, time, paramiko
from glob import glob
reload(sys)
sys.setdefaultencoding('utf-8')

# logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='AutoMumu.log', level=logging.DEBUG)
# MyLogger = logging.getLogger('simple crap')
# MyLogger.setLevel( logging.DEBUG)

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='MultiMuMu.log', level=logging.DEBUG)
MyLogger = logging.getLogger('mumulib')
MyLogger.setLevel(logging.DEBUG)

logging.getLogger("paramiko").setLevel(logging.WARNING)

def MyLogger_log_http_source():
    if os.environ.has_key('HTTP_USER_AGENT'):
        #MyLogger.info('HTTP Client: ' + os.environ['REMOTE_ADDR'] + ' (' + os.environ['REMOTE_HOST'] + ')')
        MyLogger.info('HTTP Client: ' + os.environ['REMOTE_ADDR'] + ' ')
    if os.environ.has_key('HTTP_X_FORWARDED_FOR'):
        MyLogger.info('HTTP X-For:  ' + os.environ['HTTP_X_FORWARDED_FOR'] + ' via ' + os.environ['HTTP_X_FORWARDED_HOST'])


