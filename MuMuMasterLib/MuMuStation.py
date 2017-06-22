# -*- coding: utf-8 -*-
import simplejson as json
from globals import *
from MuMuTuner import MuMuTuner

class _serializable(object):
    def serialize(self,hr=False):
        r = dict(self.__dict__)
        for k in r.keys():
            if k.startswith('_'):
                r.pop(k)
        if hr:
            return json.dumps(r, indent=4, sort_keys=True)
        return json.dumps(r)

    def deserialize(self,data):
        try:
            data = json.loads(data)
        except KeyError: # not a json
            pass
        self.__dict__.update(data)

class MuMuStation(_serializable):
    def __init__(self):
        self._tuner = None
    def set_tuner(self, tuner_instance):
        assert isinstance(tuner_instance, MuMuTuner)
        self._tuner = tuner_instance
    def get_tuner(self):
        return self._tuner


    def init(self, title, sid, freq):
        self.title = title
        self.sid = sid
        self.freq = freq

    def __eq__(self, other):
        # ignore SID by purpose - same means same freq, etc
        r = (self.freq == other.freq and \
             self.is_dvbs() == other.is_dvbs())
        if r and self.is_dvbs():
            r = (self.dvbs['diseqc']  == other.dvbs['diseqc']  and \
                 self.dvbs['pol'] == other.dvbs['pol'] and \
                 self.dvbs['srate'] == other.dvbs['srate'] )
        return r

    def is_dvbs(self):
        return self.__dict__.has_key('dvbs')

    def __make_dvbs(self):
        if not self.is_dvbs():
            self.dvbs = {'diseqc': None, 'pol': None, 'srate':None}

    def dvbs_diseqc(self, diseqc):
        self.__make_dvbs()
        self.dvbs['diseqc'] = diseqc

    def dvbs_pol(self, pol):
        self.__make_dvbs()
        self.dvbs['pol'] = pol

    def dvbs_srate(self, srate):
        self.__make_dvbs()
        self.dvbs['srate'] = srate