#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,cgi

logfile = 'MultiMuMu.log'
lines = 30
timer = 1
iteration = 1

if __name__ == "__main__":
    cgi_data = cgi.FieldStorage()
    if cgi_data.has_key('iter'):
        iteration = int(cgi_data.getvalue('iter'))
    if cgi_data.has_key('lines'):
        lines = int(cgi_data.getvalue('lines'))
    if cgi_data.has_key('timer'):
        timer = int(cgi_data.getvalue('timer'))

    print 'Content-type:text/html' + os.linesep
    print '<title>' + logfile + '</title>'
    print '<html>'
    print '<pre>'
    with open(logfile,'rb') as f:
        for l in f.readlines()[0 - lines:]:
            print l.strip()
    print '</pre>'

    print logfile + ' file size: ' + str( round(os.path.getsize(logfile)/1024.0/1024.0,1) )  + ' MByte        '

    link = 'tail_the_fail.py?lines=' + str(lines) + '&timer=' + str(timer) + '&iter='
    if iteration > 0:
        print '<b> <a href="' + link + str(-1) + '">stop</a> </b>'
        print '<b> <a href="' + link + str(iteration - 1) + '">next</a> </b>'
        print '<meta http-equiv="refresh" content="' + str(timer) + '; URL=' + link + str(iteration - 1) + '">'
    else:
        print '<b> <a href="' + link + str(128) + '">start</a> </b>'
    print '</html>'
