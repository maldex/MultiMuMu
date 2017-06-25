# MuMuMaster
Automatic distributed [MuMuDVB|http://mumudvb.net] tuning

MuMuMaster manages multipe MuMuDVB instances running against multiple DVB Tuners, supporting DVB-T and DVB-S, inclusive autoscan (w_scan)

## background
As our 'Cine S2 DVB-S2 TV Tuner' cannot run along with a 'USB DVB-T HDTV TV Tuner' on the same Linux Host due to driver incomaptibilties, we decided to solve create this



## prereqirements
```
sudo yum install -y python2-simplejson python-xmltodict python-paramiko

sudo setfacl -m u:apache:rX /home/user/
sudo setfacl -R -m u:apache:rX /home/user/MultiMuMu/
sudo touch /home/user/MultiMuMu/MultiMuMu.log
sudo chown apache:users /home/user/MultiMuMu/MultiMuMu.log
```


### proposal vhost config
```
### default vhost
<VirtualHost *:*>
    DocumentRoot /home/user/MultiMuMu
    <Directory /home/user/MultiMuMu>

        #Options     +MultiViews +Indexes +IncludesNOEXEC +SymLinksIfOwnerMatch +ExecCGI
        Options     +ExecCGI
        Require     all granted
        Options     +ExecCGI
        AddHandler  cgi-script .py
    </Directory>

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

    # additional: Server status module
    <IfModule proxy_balancer_module>
        <Location "/balancer-manager">
            SetHandler balancer-manager
        </Location>
    </IfModule>
</VirtualHost>
```



<VirtualHost *:80>
    <Location "/">
        Require ip 127.0.0.0/8 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
    </Location>
    <IfModule status_module>
        <Location /server-status>
            SetHandler server-status
        </Location>
    </IfModule>
    <IfModule proxy_balancer_module>
        <Location "/balancer-manager">
            SetHandler balancer-manager
        </Location>
    </IfModule>
    DocumentRoot /var/www/html
</VirtualHost>
