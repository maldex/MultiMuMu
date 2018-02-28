#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,cgi

logfile = 'MultiMuMu.log'

if __name__ == "__main__":
    iteration = 1
    cgi_data = cgi.FieldStorage()
    if cgi_data.has_key('iteration'):
        iteration = int(cgi_data.getvalue('iteration'))

    print 'Content-type:text/html' + os.linesep
    print '<title>' + logfile + '</title>'
    print '<html>'
    print '<pre>'
    with open(logfile,'rb') as f:
        for l in f.readlines()[-30:]:
            print l.strip()
    print '</pre>'

    print logfile + ' file size: ' + str( round(os.path.getsize(logfile)/1024.0/1024.0,1) )  + ' MByte        '

    if iteration > 0:
        print '<b> <a href="tail_the_fail.py?iteration=-1">stop</a> </b>'
        print '<meta http-equiv="refresh" content="1; URL=/tail_the_fail.py?iteration=' + str(iteration - 1) + '">'
    else:
        print '<b> <a href="tail_the_fail.py">start</a> </b>'
    print '</html>'
