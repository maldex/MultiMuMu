# MultiMuMu
Automatic distributed [MuMuDVB](http://mumudvb.net) TV tuning. You own multiple linux compatible DVB Tuners, somehow connected via TCP/IP, this project brings them together into one single 'station dialer'. Just point your favorite player [http://MultiMuMu/station=CNN+WorldWide], and get CNN. 

MultiMuMu is merely a set of python/cgi scripts that can SSH to the host w/ right dvb tuner, place a specific MuMuDVB configuration file there, kill and relaunch MuMuDVB there, and return you a 302-Moved code pointing to that host's mumudvb instance. (among some .m3u and simple list functionality)

In contrast to [HTPC](https://en.wikipedia.org/wiki/Home_theater_PC) solutions, MultiMuMu aims to be targeted by _simple_ players just following a http-url and stream it's content.
Just feed your favorite PC/iPhone/Android/raspi/SmartTV/MPEG2 or h264-http-capable-playback-software with the right url, MuMuDVB will tune and point you to there. 

If you want that, get started [here](README.get_started.md)

## simplified
```
<< HTTP:       user requests: http://MultiMuMu/i_want_to_go?station=MyFavoriteFashion_TV
XX MultiMuMu:  checks all tuners if already tuned somewhere (e.g. check all tuner for current sid)
XX MultiMuMu:  if any transponder already has sid, provide link to instance with MyFavoriteFashion_TV
XX MultiMuMu:  else: login to appropriate tuner-linux and start a mumudvb instance tuned to
>> HTTP:       Status: 302 Moved, Location HTTP://192.168.1.6:8000/bysid/2356 (mumudvb stream link)
```
This, depending on the speed mumudvb can tune on the specific hardware, takes between 0.3 and 15 seconds, while the 302-Move is delayed until mumudvb can serve via http.

## architecture
```
+-----------------+
| Linux Host A    |----+
|                 |    |    +----------------------------------------+
= DVB-T Tuner HW  |    +----| MultiMuMu Auto Tuner (Linux/apache?)   |
+-----------------+    |    | <- SSH to Tuner-HW hosts exec mumudvb  |
                       |    | -> HTTP/m3u user iface w/ 302 redirect |
+-----------------+    |    +----------------------------------------+
| Linux Host B    |----+
|                 |
= DVB-S Tuner HW  |    |
= DVB-S Tuner HW  |
+-----------------+    |
                            + - - - - - - - - +
                       + - -| (Linux Host D)  |
+ - - - - - - - - + 
 (Linux Host C)      - +    |  DVB-X Tuner HW === Satellite dish XYZ
|                 |            DVB-Y Tuner HW === Antenna ABC (e.g.directional)
= DVB-C Tuner HW            |  DVB-Z Tuner HW === Sub-Etha media receiver
= DVB-C Tuner HW  |         + - - - - - - - - +
= DVB-X Tuner HW
+ - - - - - - - - +
```
# why, in the times of WebTV?
Many WebTV (internet browser based player) require their own client software, either as app or through a browser-insance (usually some flash-player or html5 like youtube). While achieving some playback through 'any' internet connection with dynamic bandwith, they all run in user-space and are nowhere near being accelerated than though the main CPU logic. Watching web-tv just makes most browsers heavy-letargic, eats a crap load of cpu-power and therefore kills any battery sooner than necessary. (not to mention internet bandwith if multiple people watch the same programme, e.g. sport events) 

DVB in contrast is usually MPEG2 or H264. Encodings for which there's hardware around for more than ten years, and in the meanwhile it's embedded in your CPU, not only on your desktop but also in your Mobile Phone! The super-fast-super-powersaver-just-for-this-purpose-hardware is right in your hands already, WebTV in contrast just uses the main cpu core, no further acceleration. Like the times when DVD just came around and no-one had the PC-Power to watch a movie. (unless you bought a accelerated grafics ...)

in short: watch WebTV for almost two hours on one battery charge, watch DVB for six hours, with no playback device running hot, no hickups, no buffering, no constant change of quality, but with classic subtitles in teletext, with mutliple languages (if station provides), just like you're used to it from the TV Device. (do keep in mind the _constant_ bandwith. Here, i measure DVB-T ~1Mbit and DVB-S ~4Mbit, ~8Mbit for HD/h264 from Astra)

## Background
There are quite a few TV and DVB all in one solutions around, but i couldn't find one that's lightweight and provides me with a single interface to a Station, without all the frequency, technology, userinterfaces or other clutter. No recording or similar, just patch me thorugh to the stream.

I just want a interface like _http://tvbox/station=CNN+WorldWide_ which provides me with the right 302-Moved into the mumudvb. Thus achieving player-independence, making my favorite players (currently [VLC](http://videolan.org) and [RTSP Player](https://play.google.com/store/apps/details?id=org.rtspplr.app)) just eating a .m3u with my favorite stations. 

As the installation of the [Digital Devices Cine DVB-S2 V6.5](https://www.digital-devices.eu/downloads-www/cine/s/datenblatt_cine_s2_V6_dt.pdf) kernel driver renders the [Zolid Mini DVB-T Stick](https://www.linuxtv.org/wiki/index.php/Zolid_Mini_DVB-T_Stick) unusable (true story, i cannot run them on the same linux same time), i will have two tv-reception-appliances, one for DVB-T, one for DVB-S, so my solution needs to support multiple tuners in multiple linux machines. (no worries, esxi and usb/pci-passthorugh work fine on that old low power PC)

Upon a Station selection, MultiMuMuDVB uses SSH to login to linux/kernel-dvb hosts, stops any previous mumudvb instances, creates a new config file and restarts mumudvb.

# proxying
Yes, it's possible to paste all streams through apaches's mod_proxy, making your antennae network reachable from outside your private network. But won't apache explode after watching for too long?

# Experience
See the config-examples for details, actually tuning into a station via DVB-T takes around 5 secs (hard to test, only one transponder here), and between 5 to 15 seconds for DVB-S (with diseqc equipment pointed somewhere S13E0 and S19E2).

Do not neglect bandwidth, we're talking raw steady-quality TV, not some overblown, all-self-adjusting youtube- or web-stream. If your network can't handle the incoming DVB-data, the quality will not be lowered but the player will stuck. No quality resizing, but your playback device can use hardware encryption and your battery will run for hours (unlike some internet-tv apps which constantly trying to adjust the stream and fall eventually minutes behind 'live')

Also there's no locking (yet), so 'stealing' the tuner does lead into a dead-lock situation

