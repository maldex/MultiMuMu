# -*- coding: utf-8 -*-

import os, sys, logging, time, paramiko
from glob import glob
import imp
imp.reload(sys)
#sys.setdefaultencoding('utf-8')

# logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='AutoMumu.log', level=logging.DEBUG)
# MyLogger = logging.getLogger('simple crap')
# MyLogger.setLevel( logging.DEBUG)

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='/home/MultiMuMu/MultiMuMu/log/MultiMuMu.log', level=logging.DEBUG)
MyLogger = logging.getLogger('mumulib')
MyLogger.setLevel(logging.DEBUG)

logging.getLogger("paramiko").setLevel(logging.WARNING)

def MyLogger_log_http_source():
    if 'HTTP_USER_AGENT' in os.environ:
        #MyLogger.info('HTTP Client: ' + os.environ['REMOTE_ADDR'] + ' (' + os.environ['REMOTE_HOST'] + ')')
        MyLogger.info('HTTP Client: ' + os.environ['REMOTE_ADDR'] + ' ')
    if 'HTTP_X_FORWARDED_FOR' in os.environ:
        MyLogger.info('HTTP X-For:  ' + os.environ['HTTP_X_FORWARDED_FOR'] + ' via ' + os.environ['HTTP_X_FORWARDED_HOST'])


