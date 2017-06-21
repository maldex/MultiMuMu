# MuMuMaster
Automatic distributed [MuMuDVB|http://mumudvb.net] tuning

MuMuMaster manages multipe MuMuDVB instances running against multiple DVB Tuners, supporting DVB-T and DVB-S, inclusive autoscan (w_scan)

## background
As our 'Cine S2 DVB-S2 TV Tuner' cannot run along with a 'USB DVB-T HDTV TV Tuner' on the same Linux Host due to driver incomaptibilties, we decided to solve create this




cd /tmp
now=`date +%s`
satellites="S19E2 S13E0"
for s in ${satellites}; do
   for d in `seq 0 3`; do
    echo "`date` --- scanning Sat ${s} - ${d}"
    w_scan -R0 -E0 -fs -a /dev/dvb/adapter0 -s${s} -D${d}c -L > scan.`hostname`.0000.s.${s}.${d}.xspf 2>> out.${s}.${d}.txt
    delta=$((`date +%s`-$now)); echo "took: $((${delta}/3600))hrs $((${delta}/60))min $((${delta}%60))sec"
    sleep 3
   done
done
date
delta=$((`date +%s`-$now)); echo "total scan time: $((${delta}/3600))hrs $((${delta}/60))min $((${delta}%60))sec"





```
### default vhost
<VirtualHost *:80>
    <Location />
        Require ip 127.0.0.0/8 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
    </Location>
    <IfModule status_module>
        <Location /server-status>
            SetHandler server-status
        </Location>
    </IfModule>
    DocumentRoot /home/user/PycharmProjects/MuMuMaster
    <Directory /home/user/PycharmProjects/MuMuMaster>
        Options +MultiViews +Indexes +IncludesNOEXEC +SymLinksIfOwnerMatch +ExecCGI
        Require all     granted
#        DirectoryIndex  index.py
        Options +ExecCGI
        AddHandler cgi-script .py
    </Directory>
</VirtualHost>
```