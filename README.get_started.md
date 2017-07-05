# setup
This super-quick-guide assumes two machines ['dvb-s','dvb-t'] with appropriate hardware installed.
These machines find each other by name (though IP would work as well) and have both user 'user' created with 'video' group membership.

## install prereqirements
```
sudo yum install -y python2-simplejson python-xmltodict python-paramiko
sudo yum install -y httpd mod_evasive   # apache 2.4
```

## adjust permission
assuming you cloned this project as 'user'
```
sudo mkdir /home/user/MultiMuMu/config
sudo chown user:user /home/user/MultiMuMu/config
sudo setfacl -m u:apache:rX /home/user/
sudo setfacl -R -m u:apache:rX /home/user/MultiMuMu/
sudo touch /home/user/MultiMuMu/MultiMuMu.log
sudo chown apache:user /home/user/MultiMuMu/MultiMuMu.log
sudo chmod g+w /home/user/MultiMuMu/MultiMuMu.log
```

## configure apache/cgi
Please lock-down your apache yourself, the sample config here just covers a sample vhost config!
```
<VirtualHost *:*>
    DocumentRoot /home/user/MultiMuMu
    <Directory /home/user/MultiMuMu>
        Options     -Indexes +ExecCGI
        Require     all granted
        AddHandler  cgi-script .py
    </Directory>

    # additional: a dump for other M3Us
    <Directory /home/user/MultiMuMu/m3u>
        Options     +Indexes +ExecCGI
        Require     all granted
    </Directory>

    # additional: apache proxy (see exact 302 &proxy=true on tuner)
    <IfModule proxy_html_module>
        ProxyPreserveHost  Off
        ProxyRequests      On
        ProxyVia           On
        ProxyPass          /dvb-t    http://dvb-t:8499/bysid retry=0 timeout=5 connectiontimeout=20 flushpackets=on ping=1 ttl=120
        ProxyPassReverse   /dvb-t    http://dvb-t:8499/bysid
        ProxyPass          /dvb-s    http://dvb-s:8500/bysid retry=0 timeout=5 connectiontimeout=20 flushpackets=on ping=1 ttl=120
        ProxyPassReverse   /dvb-s    http://dvb-s:8500/bysid
    </IfModule>

    # additional: restrict access to private networks
    <Location />
        Require ip 127.0.0.0/8 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
    </Location>

    # additional: Server status module
    <IfModule status_module>
        <Location /server-status>
            SetHandler server-status
        </Location>
    </IfModule>

</VirtualHost>
```

# run a first scan
see [README.scan.md](README.scan.md)

# run
## tail the logs
```
sudo tail -fn0 /home/user/MultiMuMu/MultiMuMu.log /var/log/http/*
```
and access the vhost via browser

# create favorite list 'default'
a simple list of station titles
vi config/favorite.default.json
```
[ "Fashion TV", "CNN WorldWide"]
```
