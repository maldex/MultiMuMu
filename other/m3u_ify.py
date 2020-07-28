#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, glob
from glob import glob

if __name__ == "__main__":
    # print "Content-type:Application/m3u" + os.linesep
    # print 'Content-type: audio/x-mpegurl' + os.linesep
    print('Content-Disposition: attachment; filename="m3u.m3u"' + os.linesep)

    print('#EXTM3U')
    for m3u in glob('*.m3u'):
        with open(m3u,'r') as f:
            for l in f.readlines():
                if not l.startswith('#EXTM3U'):
                    print(l.strip())
