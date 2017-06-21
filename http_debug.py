#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

print "Content-type:text/html" + os.linesep
print "<html>"
for k,v in os.environ.iteritems():
    print k,'  -  ', v  , '     </br>'
print "</html>"