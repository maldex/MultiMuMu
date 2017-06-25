# MuMuMaster
Automatic distributed [MuMuDVB](http://mumudvb.net) tuning

MuMuMaster manages multipe MuMuDVB instances running against multiple DVB Tuners, supporting DVB-T and DVB-S, inclusive autoscan (w_scan)


get started [here](README.get_started.md)

# why
As our 'Cine S2 DVB-S2 TV Tuner' cannot run along with a 'USB DVB-T HDTV TV Tuner' on the same Linux Host due to driver incomaptibilties, we decided to solve create this


# MultiMuMuDVB
While [MuMuDVB](http://mumudvb.net) does a super-great job at converting DVB-TV signals into HTTP Streams (including teletext, program guide, multiple audio streams, streaming all TV services on particular transponder, etc), it cannot know where which Station is. 
MultiMuMu aims to close this bridge while providing a uniform interface among various DVB technologies.

Tuner = Harware that can recveive DVB. it can tune to a certain frequency and filter the selected SID from this transponder
Assuming you got variuos tuners, one connected to a Satellite Dish to PAKSAT, another tuner with another Dish to Eutelsat, a third one with a terrestial antenna, and maybe a fourth with Cable-TV. In this scenario we end up with four independend settop/TV/PC-Hardware. Asian Channels can only be watched in the Livingroom TV, european channels require switching the cable to the other settop-box, etc.



## http how
```
<< HTTP:       user requests: http://MultiMuMu/i_want_to_go?station=MyFavoriteFashion_TV
XX MultiMuMu:  checks all tuners if already tuned somewhere (e.g. any transponder already has sid)
XX MultiMuMu:  if not: start a mumudvb instance tuned to MyFavoriteFashion_TV (includes killing any existing instance)
>> HTTP:       Status: 302 Moved, Location HTTP://192.168.1.6:8000/bysid/2356 (mumudvb stream link)
```


# architecture
```
+-----------------+
| Linux Host A    |----+
|                 |    |   +----------------------------------------+
= DVB-T Tuner HW  |    +---| MultiMuMu Auto Tuner (Linux/apache?)   |
+-----------------+    |   | <- SSH to Tuner-HW hosts exec mumudvb  |
                       |   | -> HTTP/m3u user iface w/ 302 redirect |
+-----------------+    |   +----------------------------------------+
| Linux Host B    |----+
|                 |
= DVB-S Tuner HW  |    |
= DVB-S Tuner HW  |
+-----------------+    |
                           + - - - - - - - - - - - +
                       + - | (Linux Host D)        |
+ - - - - - - - - +
 (Linux Host C)      - +   |  DVB-X Tuner Hardware ==== Satellite dish XYZ
|                 |           DVB-Y Tuner Hardware ==== Antenna ABC (e.g.directional)
= DVB-C Tuner HW           |  DVB-Z Tuner Hardware ==== Sub-Etha media receiver
= DVB-C Tuner HW  |        + - - - - - - - - - - - +
= DVB-X Tuner HW
+ - - - - - - - - +
```
