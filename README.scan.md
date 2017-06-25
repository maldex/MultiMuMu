scanning runs via `w_scan` and is not really worked out nice.

# run a scan against a DVB-T
this will perform a simple w_scan on the remote host with dvb-t hardware
```
./MuMu_Scan --host 192.168.1.5 --user user --pass password --do_scan
```
# run a scan against a DVB-S
same, but remote host connected to DVB-S with diseqc hardware on /dev/dvb/tuner3/frontend1
```
./MuMu_Scan -H 192.168.1.5 -U user -P password --type s --tuner 0301
```

# best practices
Well, scanning is something you do once but not all the time. Figure from the Logs how the exact scan-cmd is assembled, and run something similar.
MuMu_Scan only fetches the w_scan-generated .xspf files from remote and transforms them into json.
# todo: rework scanning