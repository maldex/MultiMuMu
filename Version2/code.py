#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmltodict
from pprint import pprint

class Station():
    def __init__(self, title, freq, pol, rate, program, satno):
        self.title, self.freq, self.pol, self.rate, self.program, self.satno = title, freq, pol, rate, program, satno



f = open("Hotbird.0c.xml")

namespaces=namespaces
pprint(xmltodict.parse(f.read(), process_namespaces=True))
# for entry in xmltodict.parse(f.read())['playlist']['trackList']['track']:
#     pprint(entry['extension']['vlc:option'])
#     myStation = Station(title=entry['title'],
#                         freq=entry['location'].split('=')[-1])
#     pprint(myStation)
#     break
