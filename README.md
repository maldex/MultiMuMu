# MuMuMaster
Automatic distributed [MuMuDVB](http://mumudvb.net)  tuning

MuMuMaster manages multipe MuMuDVB instances running against multiple DVB Tuners, supporting DVB-T and DVB-S, inclusive autoscan (w_scan)

# why
As our 'Cine S2 DVB-S2 TV Tuner' cannot run along with a 'USB DVB-T HDTV TV Tuner' on the same Linux Host due to driver incomaptibilties, we decided to solve create this

# how
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