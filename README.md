# MuMuMaster
Automatic distributed [MuMuDVB](http://mumudvb.net)  tuning

MuMuMaster manages multipe MuMuDVB instances running against multiple DVB Tuners, supporting DVB-T and DVB-S, inclusive autoscan (w_scan)

# why
As our 'Cine S2 DVB-S2 TV Tuner' cannot run along with a 'USB DVB-T HDTV TV Tuner' on the same Linux Host due to driver incomaptibilties, we decided to solve create this


# how
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

                       |
+ - - - - - - - - +
 (Linux Host C)      - +
|                 |
= DVB-C Tuner HW
= DVB-C Tuner HW  |
= DVB-X Tuner HW
+ - - - - - - - - +
```