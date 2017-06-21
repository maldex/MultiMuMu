# -*- coding: utf-8 -*-
from urllib import quote_plus
from globals import *
from MuMuStation import MuMuStation

class RenderCLI(object):
    def __init__(self):
        pass

    def title(self, s):
        print "-= " + s + " =-"

    def table_begin(self):
        pass

    def table_entry(self,s):
        assert isinstance(s, MuMuStation)
        print s.get_tuner().ssh.host + '\t' + s.title + '\t' + str(s.freq)

    def table_end(self):
        pass

    def link_tune_to(self,s):
        if os.environ.has_key('HTTP_USER_AGENT'):
            return 'http://' + os.environ['HTTP_HOST'] + '/MuMu_Tune.py?station=' + quote_plus(s.title.encode('utf-8'))
        else:
            return 'python MuMu_Tune.py --station "' + s.title + "'"


class RenderM3U(RenderCLI):
    def __init__(self):
        super(self.__class__, self).__init__()
        if os.environ.has_key('HTTP_USER_AGENT'):
            print "Content-type:Application/m3u" + os.linesep

    def title(self,s):
        pass

    def table_begin(self):
        print '#EXTM3U'

    def table_entry(self,s):
        assert isinstance(s, MuMuStation)
        print '#EXTINF:-1,' + s.title
        print self.link_tune_to(s)

    def table_end(self):
        pass

class RenderCGI(RenderCLI):
    def __init__(self):
        super(self.__class__, self).__init__()
        print "Content-type:text/html" + os.linesep

    def title(self, s):
        m3u_link = os.environ['REQUEST_URI']
        if m3u_link.find('?') > 0:
            m3u_link += '&'
        else:
            m3u_link += '?'
        m3u_link = m3u_link + 'format=m3u'
        print '<h3> <a href="' + m3u_link + '">' + s + '</a> </h3>' + os.linesep

    def table_begin(self):
        print '<table style="width:100%">'
        print '<tr> ' + \
              '<td><b>m3u</b></td> ' + \
              '<td><b>direct</b></td> ' + \
              '<td><b>host/tuner</b></td> ' + \
              '<td><b>freq</b></td> ' + \
              '<td><b>pol</b></td> ' + \
              '<td><b>srate</b></td> ' + \
              '<td><b>DiSEqC</b></td> ' + \
              '</tr>'

    def table_entry(self, s):
        assert isinstance(s, MuMuStation)
        print '  <tr>',
        l = '<a href="' + self.link_tune_to(s) + '">' + 'direct' + '</a>'
        l2 = '<a href="' + os.environ['SCRIPT_NAME'] + '?format=m3u&pretune=true&bouquet='+ quote_plus(s.title.encode('utf-8'))   + '">' + s.title + '</a>'
        cols = [l2, l, s.get_tuner().ssh.host + '/' + s.get_tuner().tuner, s.freq]
        if s.is_dvbs():
            cols += [ s.dvbs['pol'], s.dvbs['srate'],s.dvbs['diseqc']]
        for e in cols:
            print '<td>' + str(e) + '</td>',
        print '</tr>'

    def table_end(self):
        print '</table>'