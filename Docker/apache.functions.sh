#!/bin/bash
# 
### 
# this document describes a common semi-automated apache installation on CentOS/Redhat 7+. It's grouped into functions:
#   1.  function 'apache_install_all'
#   2.  function 'apache_minimum_modules'
#   3.  function 'apache_default_vhost'
#   4.  function 'apache_lil_tweaks'
#   5.  function 'apache_enable_proxy'
#   6.  function 'apache_enable_balancer'
#   7.  function 'apache_enable_ssl'

# keep your C:\Windows\System32\drivers\etc\hosts handy

certpath=/etc/httpd/certs

cd /etc/httpd 2> /dev/null

function _apache_module_enabler() {
    pushd /etc/httpd >/dev/null
    echo ">>>> enable apache module '$1'"
    sed -i '/'$1'/s/^#;//' conf.modules.d/*
    popd >/dev/null
}

function apache_install_all() {    
    
    if ! yum provides mod_evasive; then echo "CANNOT ADD MOD EVASIVE"; fi
    
    echo ">>> install apache and modules"
    yum install -y httpd mod_evasive mod_security mod_proxy_html mod_ssl
     
    cd /etc/httpd
    echo ">>> whyever, mod_evasive ends up in the wrong directory"
    mv -v conf.d/mod_evasive.conf conf.modules.d/
    mv -v conf.d/mod_security.conf conf.modules.d/
     
    echo ">>> enable apache start at system startup and allow firewall"
    #systemctl enable httpd
    #firewall-cmd --zone=public --add-service=http --permanent
    #firewall-cmd --zone=public --add-service=https --permanent
    #firewall-cmd --reload
     
    echo ">>> create a copy of default config"
    tar -zcf ~/http-orig.tgz /var/www /etc/httpd
     
    echo ">>> allow 'wheel' everywhere"
    setfacl -d -m g:wheel:rwX /var/log/httpd
    echo ">>> also on config and docroot, but limit apache to read-only"
    for dir in /etc/httpd /var/www; do
        chown -v -R root:wheel ${dir}
        find ${dir} -type f -exec chmod -v 660 {} \;
        find ${dir} -type d -exec chmod -v 02770 {} \;
        setfacl -R -m g:wheel:rwX -m g:apache:rX ${dir}
        setfacl -d -R -m g:wheel:rwX -m g:apache:rX ${dir}
        done
    cd /etc/httpd
    echo ">>> function ${FUNCNAME[0]} done"
}

function apache_minimum_modules() {
    cd /etc/httpd
    # minimum modules
    MODULES="systemd_module access_compat_module actions_module alias_module allowmethods_module auth_basic_module auth_digest_module"
    MODULES+=" authn_anon_module authn_core_module authn_file_module authz_core_module authz_groupfile_module authz_host_module" 
    MODULES+=" authz_user_module data_module deflate_module dir_module echo_module env_module expires_module ext_filter_module filter_module"
    MODULES+=" headers_module include_module log_config_module logio_module mime_magic_module mime_module negotiation_module remoteip_module"
    MODULES+=" reqtimeout_module rewrite_module setenvif_module substitute_module unique_id_module unixd_module version_module"
    MODULES+=" vhost_alias_module log_debug_module log_debug_module mod_slotmem_shm"
    #MODULES+=" status_module dumpio_module cache_disk_module cache_module"
     
    echo ">>> disable ALL module config"
    sed -i '/^#;/!s/^/#;/' conf.d/autoindex.conf
    sed -i '/^#;/!s/^/#;/' conf.d/userdir.conf
    sed -i '/^#;/!s/^/#;/' conf.d/welcome.conf
    sed -i '/^#;/!s/^/#;/' conf.d/ssl.conf
    sed -i '/^#;/!s/^/#;/' conf.modules.d/*
          
    echo ">>> re-enable MPM and CGI"
    sed -i 's/^#;//' conf.modules.d/00-mpm.conf
    sed -i 's/^#;//' conf.modules.d/01-cgi.conf
    sed -i 's/^#;//' conf.modules.d/mod_evasive.conf
     
    echo ">>> re-enable minimal requiered modules"
    for module in ${MODULES}; do
        _apache_module_enabler ${module}
    done
     
    echo ">>> check module config (this should NOT throw an module related error)"
    httpd -M
    echo ">>> function ${FUNCNAME[0]} done"
}

function apache_lil_tweaks() {
    cd /etc/httpd
    _apache_module_enabler mod_autoindex
    _apache_module_enabler status_module
    # lil nice-ness
    sed -i 's/FancyIndexing/FancyIndexing NameWidth=*/g' conf.d/autoindex.conf
    sed -i 's/^#;//g' conf.d/autoindex.conf
    httpd -S #&& systemctl restart httpd
}

function apache_default_vhost(){
    LOGFORMAT='"%a %h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\""'
    SERVERADMIN=some@whre
    SERVERNAME="default-vhost-on-`hostname -s`"
     
    cd /etc/httpd
         
    echo ">>> configure ServerAdmin and Servername, and default vhost(s)"
    sed -i 's/^ServerAdmin .*/ServerAdmin '"${SERVERADMIN}"'/g' conf/httpd.conf
    sed -i 's/^#ServerName .*/ServerName '"${SERVERNAME}"'/g' conf/httpd.conf
    sed -i 's/^EnableSendfile .*/EnableSendfile off/' conf/httpd.conf # when serving from nfs
        
    # disable conf.d/ include at this point
    sed -i '/^IncludeOptional.*conf.d\/\*.conf/s/^/# -- first the default vhost here, then include custom vhosts -- # /' conf/httpd.conf
     
    # insert custom properties, and the default vhost
    echo "# additional custom settings
ServerSignature              Off
ServerTokens                 Prod
 
UseCanonicalName             Off
DeflateCompressionLevel      9
HostnameLookups              on
RemoteIPHeader               X-Forwarded-For
LogFormat                    ${LOGFORMAT} proxy
#ErrorLog                    \"| /usr/bin/logger -t httpd-default -i -p local5.error\"
#CustomLog                   \"| /usr/bin/logger -t httpd-default -i -p local5.notice\"  proxy
 
# increase these values for your vhost
RequestHeader                set Connection close
LimitRequestBody             32
LimitXMLRequestBody          32
Timeout                      1
Options                      -ExecCGI -FollowSymLinks -Indexes -MultiViews
 
# DEFAULT VHOST: if no other ServerName or ServerAlias matches to the requested url

<VirtualHost *:80> # default port 80 vhost
    <Location \"/\">
        Require ip           127.0.0.0/8 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
    </Location>
    <IfModule status_module>
        <Location /server-status>
            SetHandler server-status
        </Location>
    </IfModule>
    <IfModule proxy_balancer_module>
        <Location \"/balancer-manager\">
            SetHandler balancer-manager
        </Location>
    </IfModule>
    DocumentRoot /var/www/html
</VirtualHost>
 
<IfModule ssl_module>
    Listen                       443         https
    SSLPassPhraseDialog          exec:/usr/libexec/httpd-ssl-pass-dialog
    SSLSessionCache              shmcb:/run/httpd/sslcache(512000)
    SSLSessionCacheTimeout       300
    SSLRandomSeed                startup     file:/dev/urandom  2048
    SSLRandomSeed                connect     file:/dev/urandom  2048
    SSLCryptoDevice              builtin
     
    <VirtualHost *:443> # default port 443 vhost
        SSLEngine                on
        SSLProtocol              all -SSLv2 -SSLv3 -TLSV1
        SSLCipherSuite           EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH
        SSLHonorCipherOrder      on
        SSLCertificateChainFile  /etc/httpd/certs/default.ca-crt
        SSLCertificateFile       /etc/httpd/certs/default.crt
        SSLCertificateKeyFile    /etc/httpd/certs/default.key
        # default ssl-vhost: redirect back to the non-ssl variant of your request
        RewriteEngine            on
        RewriteCond              %{HTTPS}    on
        RewriteRule              (.*)        http://%{HTTP_HOST}%{REQUEST_URI} [R=temp,L]
    </VirtualHost>
</IfModule>
 
IncludeOptional              conf.d/*.conf
" >> conf/httpd.conf
     
    echo ">>> creating default /var/www/html/index.html"
    echo "<title>`hostname -s`</title>
    <h1>default vhost on `hostname` </h1><br>
    Apache: <a href=/server-status>server-status</a> <br>" >> /var/www/html/index.html

    echo ">>> list vhost config (httpd -S) and restart apache"
    httpd -S #&& systemctl restart httpd
    echo "GOTO HTTP://`hostname -f`"
    echo ">>> function ${FUNCNAME[0]} done"
}

function apache_enable_proxy(){
    _apache_module_enabler proxy_module
    _apache_module_enabler proxy_http_module
    _apache_module_enabler proxy_html
    _apache_module_enabler mod_proxy
    _apache_module_enabler mod_proxy_connect
    _apache_module_enabler mod_proxy_http
    _apache_module_enabler mod_proxy_wstunnel
    _apache_module_enabler mod_watchdog
    echo ">>> placing demo-vhost into conf.d/vhost-simple-proxy.conf"
    echo "# sample vhost for simple proxy
<VirtualHost *:80>
    ServerName                   simple.`hostname -f`
    ServerAlias                  simple.`hostname -s` simple.localhost simple.your.domain
    
    # https://httpd.apache.org/docs/2.4/mod/mod_proxy.html
    ProxyRequests                Off
    ProxyVia                     Off

    ProxyPass                    /               http://10.86.33.23:8090/
    ProxyPassReverse             /               http://10.86.33.23:8090/
    
    # same through balancer
    #ProxyPass                    /balancer-manager       !
    #<Location /balancer-manager>
    #    SetHandler               balancer-manager
    #</Location>
    #
    #ProxyPass                     /              balancer://simple-backend/
    #ProxyPassReverse              /              balancer://simple-backend/
    #
    #<Proxy balancer://simple-backend>
    #    BalancerMember           http://10.86.33.23:8090
    #</Proxy>
</VirtualHost> " > conf.d/vhost-simple-proxy.conf

    echo ">>> list vhost config (httpd -S) and restart apache"
    httpd -S # && systemctl restart httpd
    echo "GOTO HTTP://simple.your.domain"
    echo ">>> don't forget about  'tail -fn0 /var/log/httpd/*_log'  when testing"
    echo ">>> function ${FUNCNAME[0]} done"
}

function apache_enable_balancer(){
    _apache_module_enabler proxy_balancer_module
    _apache_module_enabler slotmem_plain_module
    _apache_module_enabler slotmem_shm_module
    _apache_module_enabler socache_shmcb_module
    _apache_module_enabler xml2enc_module
    _apache_module_enabler lbmethod_bybusyness_module
    _apache_module_enabler lbmethod_byrequests_module
    _apache_module_enabler lbmethod_bytraffic_module
    _apache_module_enabler lbmethod_heartbeat_module
    echo ">>> TODO: edit conf.d/vhost-simple-proxy.conf"
    echo ">>> TODO: restart your apache   'httpd -S && systemctl restart httpd; tail -fn0 /var/log/httpd/*_log'"
    echo "GOTO HTTP://simple.your.domain/balancer-manager"
    echo ">>> function ${FUNCNAME[0]} done"
}

function apache_enable_ssl(){
    echo ">>> create some self-signed certificates for default vhosts"
    if [ ! -e /etc/httpd/certs ]; then 
        mkdir /etc/httpd/certs
        echo ">>> created an Authority (passwords won't matter and won't be used further, just type asdfasdf)"
        CreateSelfSignedAuthority
        echo ">>> created an Certificate (passwords won't matter and won't be used further, just type asdfasdf)"
        CreateSelfSignedCertificate
    fi

    _apache_module_enabler ssl_module 
    _apache_module_enabler socache_shmcb_module

    httpd -S # && systemctl restart httpd
    echo "GOTO HTTPS://`hostname -f`"
    echo ">>> function ${FUNCNAME[0]} done"
}

function apache_mkComplexProxy() {
    CreateSelfSignedCertificate complex.your.domain
    echo "# # http-to-https redirect vhost
<VirtualHost *:80>
        ServerName              complex.localhost
        ServerAlias             complex.localhost complex.localhost complex.your.domain

        # push to https
        RewriteEngine           On
        RewriteRule             (.*)   https://%{HTTP_HOST}%{REQUEST_URI}
</VirtualHost>

# THE vhost that counts
<VirtualHost *:443>
# ssl/tls
        SSLEngine               on
        SSLProtocol             all -SSLv2 -SSLv3 -TLSV1
        SSLHonorCipherOrder     on
        SSLCipherSuite          EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH
        SSLCertificateChainFile /etc/httpd/certs/default.ca-crt
        SSLCertificateFile      /etc/httpd/certs/complex.your.domain.crt
        SSLCertificateKeyFile   /etc/httpd/certs/complex.your.domain.key

# globals
        ServerName              complex.localhost
        ServerAlias             complex.localhost complex.localhost complex.your.domain
        ErrorLog                logs/proxy-confluence_error_log
        CustomLog               logs/proxy-confluence_access_log combined

        LimitRequestBody        104857600
        LimitXMLRequestBody     104857600
        Timeout                 300
        KeepAlive               On
        KeepAliveTimeout        0

# remote management
        <IfModule status_module>
                ProxyPass               /server-status          !
                <Location               /server-status>
                        SetHandler      server-status
                        Require ip      127.0.0.0/8 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
                </Location>
        </IfModule>
        <IfModule proxy_balancer_module>
                ProxyPass               /balancer-manager       !
                <Location               /balancer-manager>
                        SetHandler      balancer-manager
                        Require ip      127.0.0.0/8 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
                </Location>
        </IfModule>

# reverse proxy settings
        # https://httpd.apache.org/docs/2.4/mod/mod_proxy.html
        ProxyRequests           Off
        ProxyVia                Off
        ProxyPreserveHost       On
        SSLProxyEngine          On

# here the application-specific config begins
        <Location /synchrony>
            Require all granted
            RewriteEngine on
            RewriteCond %{HTTP:UPGRADE} ^WebSocket$ [NC]
            RewriteCond %{HTTP:CONNECTION} Upgrade$ [NC]
            RewriteRule .* ws://127.0.0.2:8091%{REQUEST_URI} [P]
        </Location>

# reverse-proxy mappings
        ProxyPass           /           balancer://backend-confluence/tiles
        ProxyPassReverse    /           balancer://backend-confluence/tiles

# reverse-proxy-backends
        # proxy-sided add cookie to map back-end member server (ROUTEID=route)
        Header                  add Set-Cookie  "ROUTEID=.%{BALANCER_WORKER_ROUTE}e; path=/" env=BALANCER_ROUTE_CHANGED
        <Proxy balancer://backend-confluence>
                ProxySet        stickysession=ROUTEID
                ProxySet        failonstatus=500,501,502,503
                ProxySet        lbmethod=byrequests
                BalancerMember  http://127.0.0.2:8080 route=instance1 flushpackets=On  keepalive=On  connectiontimeout=5  timeout=300  ping=3  retry=30
        </Proxy>
</VirtualHost>
" > conf.d/vhost-complex-proxy.conf
    httpd -S # && systemctl restart httpd
    echo ">>> function ${FUNCNAME[0]} done"
}

function CreateSelfSignedAuthority(){
    pushd ${certpath} > /dev/null
    if [ -e default.ca-crt ]; then 
        echo "default certificate authority already exists"
        return 2; 
    fi
 
    export COMPANY="Self-Signed Certificate Authority at `hostname -f`"
    export DOMAIN="`hostname -f`"
 
    # generate CA Key
    openssl genrsa -aes256 -out default.ca-key.org 2048
 
    # unlocking CA Key - not sure this is a good idea
    openssl rsa -in default.ca-key.org -out default.ca-key
    rm -f default.ca-key.org
 
    # generating certificate
    openssl req -new -x509 -days 3650 -key default.ca-key -out default.ca-crt -subj "/C=ZZ/ST=selfsigned/L=host `hostname`/O=Private Zertifikazion Master Blaster Schtelle/OU=we issue certificates for others/CN=${DOMAIN}/emailAddress=does@not.exist/subjectAltName=DNS.1=${DOMAIN},DNS.2=*.${DOMAIN}"
 
    # insepct this certificate
    #openssl x509 -in default.ca-crt -text -nooutll
    popd > /dev/null
}

function CreateSelfSignedCertificate(){
    pushd ${certpath} > /dev/null
    THISSITE=$1
    if [ "${THISSITE}" == "" ]; then
        THISSITE=default
    fi
       
    # generate key
    openssl genrsa -aes256 -out ${THISSITE}.key.org 2048
        
    openssl rsa -in ${THISSITE}.key.org -out ${THISSITE}.key
        
    # generate CSR
    openssl req -new -key ${THISSITE}.key -out ${THISSITE}.csr -subj "/C=CH/ST=ZH/L=ZH/O=Private Serdificat from da Master Blaster Schtelle/OU=we got this from the local CA/CN=${THISSITE}/emailAddress=no@one.here/subjectAltName=DNS.1=${THISSITE},DNS.2=*.${THISSITE}"
        
    # signing against CA from above
    openssl x509 -req -in ${THISSITE}.csr -out ${THISSITE}.crt -sha256 -CA default.ca-crt -CAkey default.ca-key -CAcreateserial -days 1825
 
    rm -f ${THISSITE}.csr *.srl ${THISSITE}.key.org
 
    # inspect
    #openssl x509 -in ${THISSITE}.crt -text -noout
    popd > /dev/null
}


## increase semaphores - apache mod_proxy reports 'no space left on device'
## see current settings / limits
#ipcs -l
# 
## clean up last semaphores
#ipcrm sem $(ipcs -s | grep apache | awk '{print$2}')
# 
#echo ">>> increase semaphores
#kernel.msgmni = 1024
#kernel.sem = 1500 256000 32 4096
#">> /etc/sysctl.conf
# 
#sysctl -p
 
certpath=/etc/httpd/certs


function old_apache_install_minimal(){
    ##############################################################################
    # defaults
    ##############################################################################
    LOGFORMAT='"%a %h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\""'
    SERVERADMIN="no@bo.dy"
    SERVERNAME=`hostname`
    MODULES="systemd_module access_compat_module actions_module alias_module allowmethods_module auth_basic_module auth_digest_module authn_anon_module authn_core_module authn_file_module authz_core_module authz_groupfile_module authz_host_module authz_user_module data_module deflate_module dir_module echo_module env_module expires_module ext_filter_module filter_module headers_module include_module log_config_module logio_module mime_magic_module mime_module negotiation_module remoteip_module reqtimeout_module rewrite_module setenvif_module status_module substitute_module unique_id_module unixd_module version_module vhost_alias_module log_debug_module log_debug_module mod_slotmem_shm"
    #MODULES+=" dumpio_module cache_disk_module cache_module" 


    ##############################################################################
    # install apache
    ##############################################################################
    # do not yet install mod_ssl or mod_proxy_html!!
    yum install -y httpd mod_evasive  whois
    # systemctl enable httpd

    # fixing permissions
    setfacl -d -m g:wheel:rwX /var/log/httpd 
    for dir in /etc/httpd /var/www; do
        chown -R root:wheel ${dir}
        find ${dir} -type f -exec chmod 660 {} \;
        find ${dir} -type d -exec chmod 02770 {} \; 
        setfacl -R -m g:wheel:rwX -m g:apache:rX ${dir}
        setfacl -d -R -m g:wheel:rwX -m g:apache:rX ${dir}
        done


    ##############################################################################
    # harden apache
    ##############################################################################
    cd /etc/httpd
     
    # configure defaults
    sed -i 's/^ServerAdmin .*/ServerAdmin '"${SERVERADMIN}"'/g' conf/httpd.conf
    sed -i 's/^#ServerName .*/ServerName '"${SERVERNAME}"'/g' conf/httpd.conf
    sed -i 's/^EnableSendfile .*/EnableSendfile off/' conf/httpd.conf # when serving from nfs
    
    # disable conf.d/ include
    sed -i '/^IncludeOptional.*conf.d\/\*.conf/s/^/#### custom default vhost before    /' conf/httpd.conf
    if [ -e /opt/v3tk/env_my.sh ]; then
        /opt/v3tk/env_my.sh apache
        echo "Include conf/env_my.conf" >> conf/httpd.conf
    fi
    echo ">>> some more custom stuff
ServerSignature              Off
ServerTokens                 Prod
    
UseCanonicalName             Off
DeflateCompressionLevel      9
HostnameLookups              on
RemoteIPHeader               X-Forwarded-For
LogFormat                    ${LOGFORMAT} proxy
#ErrorLog                    \"| /usr/bin/logger -t httpd-default -i -p local5.error\"
#CustomLog                   \"| /usr/bin/logger -t httpd-default -i -p local5.notice\"  proxy
LimitRequestBody             1024

<VirtualHost *:80>   # DEFAULT VHOST: if no other ServerName or ServerAlias matches to the requested url
    <Location \"/\">
        Require ip           127.0.0.0/8 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
    </Location>
    <IfModule status_module>
        <Location /server-status>
            SetHandler server-status
        </Location>
    </IfModule>
    <IfModule proxy_balancer_module>
        <Location \"/balancer-manager\">
            SetHandler balancer-manager
        </Location>
    </IfModule>
    DocumentRoot /var/www/html
</VirtualHost>

IncludeOptional              conf.d/*.conf
" >> conf/httpd.conf

    ##############################################################################
    # create default vhost index
    ##############################################################################
    echo "<title>`hostname -s`</title>
    <h1>default vhost on `hostname` </h1><br>
    Apache: <a href=/server-status>server-status</a> <br>" >> /var/www/html/index.html

    ##############################################################################
    # mess with the modules
    ##############################################################################
    # disable ALL module config 
    sed -i '/^#;/!s/^/#;/' conf.d/autoindex.conf
    sed -i '/^#;/!s/^/#;/' conf.d/userdir.conf
    sed -i '/^#;/!s/^/#;/' conf.d/welcome.conf
    sed -i '/^#;/!s/^/#;/' conf.modules.d/*
     
    # re-enable certain configs fully
    sed -i 's/^#;//' conf.modules.d/00-mpm.conf
    sed -i 's/^#;//' conf.modules.d/01-cgi.conf

    # re-enable some modules
    for m in ${MODULES}; do
        sed -i '/'${m}'/s/^#;//' conf.modules.d/*
    done

    # restarting and printing config
    httpd -S #&& systemctl restart httpd
    echo "GOTO HTTP://`hostname -f`"
}

function apache_ease_evasive() {
    cd /etc/httpd
    cp conf.d/mod_evasive.conf conf.d/mod_evasive.conf.`date +%Y%m%d-%H%M%S`
    sed -i 's/DOSHashTableSize .*/DOSHashTableSize 30000/g' conf.d/mod_evasive.conf
    sed -i 's/DOSPageCount .*/DOSPageCount 10/g' conf.d/mod_evasive.conf
    sed -i 's/DOSSiteCount .*/DOSSiteCount 150/g' conf.d/mod_evasive.conf
    sed -i 's/DOSBlockingPeriod .*/DOSBlockingPeriod 5/g' conf.d/mod_evasive.conf
    httpd -S #&& systemctl restart httpd
}

function old_apache_enable_autoindex() {
    cd /etc/httpd
    # lil nice-ness
    sed -i 's/FancyIndexing/FancyIndexing NameWidth=*/g' conf.d/autoindex.conf
    sed -i 's/^#;//g' conf.d/autoindex.conf
    sed -i '/mod_autoindex/s/^#;//' conf.modules.d/*
    httpd -S #&& systemctl restart httpd
}

function old_apache_enable_php55() {
    # install PHP
    rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm
    yum install -y php55w php55w-intl php55w-opcache php55w-mysql php55w-mbstring php55w-bcmath php55w-soap php55w-gd php55w-xml
     
    # configure PHP
    sed -i 's?;date.timezone =?date.timezone = Europe/Zurich?g' /etc/php.ini
    sed -i 's/^#;//' /etc/httpd/conf.modules.d/10-php.conf
     
    # default php site in default vhost
    echo "<html>
    <head> <title>PHP Info</title> </head>
    <body> <?php phpinfo(); ?> </body>
    </html>" >/var/www/html/info.php
    echo"PHP: <a href=/info.php>info.php</a><br>"  >> /var/www/html/index.html
    httpd -S # && systemctl restart httpd
    echo "GOTO HTTP://`hostname -f`/info.php"
}

function old_apache_enable_composer120() {
    echo " >> installing composer"
    pushd /usr/local/src
    php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
    php composer-setup.php --filename=composer --install-dir=/usr/local/bin  --version=1.2.0
    rm -f composer-setup.php  # remove installer
    popd
}

function old_apache_enable_proxy() {
    cd /etc/httpd
    echo 'getbutik:$apr1$dpEVD..T$vr5fbQyFB6Af.7qQJGEE2.' > protected.htpasswd
    echo ">>> getbutik:preview
<Location />
    <RequireAny>
        <RequireAll>
            Require expr     %{REQUEST_URI} =~ m#(^/someUrl/.*|^/someMoreUrl$)#
        </RequireAll>
        AuthType              Basic
        AuthName              \"getbutik preview protected on `hostname -s`\"
        AuthUserFile         protected.htpasswd
        Require              valid-user
    </RequireAny>
</Location>" > protected.conf

    yum install -y mod_proxy_html

    sed -i '/slotmem_plain_module/s/^#;//' conf.modules.d/* 
    sed -i '/slotmem_shm_module/s/^#;//' conf.modules.d/* 
    sed -i '/socache_shmcb_module/s/^#;//' conf.modules.d/* 
    sed -i '/xml2enc_module/s/^#;//' conf.modules.d/* 
    sed -i '/lbmethod_bybusyness_module/s/^#;//' conf.modules.d/* 
    sed -i '/lbmethod_byrequests_module/s/^#;//' conf.modules.d/* 
    sed -i '/lbmethod_bytraffic_module/s/^#;//' conf.modules.d/* 
    sed -i '/lbmethod_heartbeat_module/s/^#;//' conf.modules.d/* 
    sed -i '/proxy_module/s/^#;//' conf.modules.d/* 
    sed -i '/proxy_balancer_module/s/^#;//' conf.modules.d/* 
    sed -i '/proxy_http_module/s/^#;//' conf.modules.d/* 

    echo ">>> demonstration of a simple http reverse proxy
<VirtualHost *:80>
    #Include                  protected.conf          # htpass-protection
    ServerName               asdf.`hostname -f`
    ServerAlias              asdf.`hostname -s` 
    ErrorLog                 logs/proxy-asdf_error_log
    CustomLog                logs/proxy-asdf_access_log combined
    
    # Proxy specific settings
    ProxyPreserveHost        On
    ProxyRequests            On
    ProxyVia                 On
    #SSLProxyEngine           On   # enable if backend server is HTTPS
    
    # backend server
    ProxyPass                /    balancer://asdf-blancer/
    ProxyPassReverse         /    balancer://asdf-blancer/
    
    # backend balancer configuration 
    Header add Set-Cookie    \"ROUTEID=.%{BALANCER_WORKER_ROUTE}e; path=/\" env=BALANCER_ROUTE_CHANGED
    <Proxy balancer://asdf-blancer>
        # note: route number to balancermember is just a random number, not a priority
        ProxySet             stickysession=ROUTEID
        BalancerMember       http://www.asdf.com   connectiontimeout=3 timeout=10   route=1567
        #BalancerMember      http://www.asdf.ch    connectiontimeout=3 timeout=10   route=6543
        #BalancerMember      ....
    </Proxy>
</VirtualHost>
" > conf.d/vhost-demo-proxy.conf
    echo "Apache: <a href=/balancer-manager>balancer-managers</a> <br>" >> /var/www/html/index.html

    httpd -S # && systemctl restart httpd   
    echo "GOTO HTTP://asdf.`hostname -f`, see conf.d/vhost-demo-proxy.conf"
}

function old_apache_enable_ssl(){
    cd /etc/httpd
    csuite='"EECDH+ECDSA+AESGCM EECDH+aRSA+AESGCM EECDH+ECDSA+SHA384 EECDH+ECDSA+SHA256 EECDH+aRSA+SHA384 EECDH+aRSA+SHA256 EECDH+aRSA+RC4 EECDH EDH+aRSA HIGH MEDIUM !aNULL !MD5 !SEED !IDEA !SSLv3 !SSLv2 !TLSv1"'
    yum install -y mod_ssl
    # disable default ssl-config, it's crap
    sed -i '/^#;/!s/^/#;/' conf.d/ssl.conf
    # move default-ssl-vhost before the includes
    sed -i '/^IncludeOptional.*conf.d\/\*.conf/s/^/#### custom default ssl vhost before     /' conf/httpd.conf
    echo ">>> load SSL Module  
Listen                       443 https
SSLPassPhraseDialog          exec:/usr/libexec/httpd-ssl-pass-dialog
SSLSessionCache              shmcb:/run/httpd/sslcache(512000)
SSLSessionCacheTimeout       300
SSLRandomSeed startup        file:/dev/urandom  1024
SSLRandomSeed connect        builtin
SSLCryptoDevice              builtin
<VirtualHost *:443> # DEFAULT VHOST FOR TLS/SSL: rewrite address from HTTPS:// to HTTP://
    SSLEngine                on
    SSLProtocol              all -SSLv2 -SSLv3 -TLSV1
    SSLCipherSuite           ${csuite}
    SSLHonorCipherOrder      on
    SSLCertificateChainFile  ${certpath}/default.ca-crt
    SSLCertificateFile       ${certpath}/default.crt
    SSLCertificateKeyFile    ${certpath}/default.key
    # default ssl-vhost: redirect back to the non-ssl variant of your request
    RewriteEngine            on
    RewriteCond              %{HTTPS}    on
    RewriteRule              (.*)        http://%{HTTP_HOST}%{REQUEST_URI} [R=temp,L]
</VirtualHost>
IncludeOptional              conf.d/*.conf
" >> conf/httpd.conf

    mkdir ${certpath}
    chown -R root:wheel ${certpath}
    chmod 02775 ${certpath}

    # generating certificates
    echo "generating Self-Signed Authority"
    CreateSelfSignedAuthority
    echo "generating Self-Signed Certificate"
    CreateSelfSignedCertificate

    echo ">>> demonstration of a simple https vhost
<VirtualHost *:80>   # non-ssl variant of this vhost: redirect to https
    ServerName              ssl.`hostname -f`
    ServerAlias             ssl.`hostname -s`
    RewriteEngine           On
    RewriteCond             %{HTTPS}    off
    RewriteRule             (.*)        https://%{HTTP_HOST}%{REQUEST_URI} [R=permanent,L]
</VirtualHost>
<VirtualHost *:443>  # HTTPS vhost
    Include                 protected.conf
    ServerName              ssl.`hostname -f`
    ServerAlias             ssl.`hostname -s`
    ErrorLog                logs/ssl-`hostname -s`_error_log
    CustomLog               logs/ssl-`hostname -s`_access_log      combined
    SSLEngine               on
    SSLProtocol             all -SSLv2 -SSLv3 -TLSV1
    SSLCipherSuite          ${csuite}
    SSLHonorCipherOrder     on
    SSLCertificateChainFile ${certpath}/default.ca-crt
    SSLCertificateFile      ${certpath}/default.crt
    SSLCertificateKeyFile   ${certpath}/default.key
    
    <Directory /var/www/html>
        Options -MultiViews -Indexes +IncludesNOEXEC +SymLinksIfOwnerMatch +ExecCGI
        Require all granted
        # AllowOverride All activates .htaccess files
        AllowOverride   All
    </Directory>
</VirtualHost>
" > conf.d/vhost-demo-ssl.conf
    httpd -S # && systemctl restart httpd   
    echo "GOTO HTTP://ssl.`hostname -f`, see conf.d/vhost-demo-ssl.conf"
}

function _apache_add_sshtunnel(){
# https://nurdletech.com/linux-notes/ssh/via-http.html     http://dag.wiee.rs/howto/ssh-http-tunneling/
_apache_module_enabler mod_proxy
_apache_module_enabler mod_proxy_connect
_apache_module_enabler mod_proxy_http

# add something like the below to your DEFAULT VHOST
# ohther vhost wont work 
echo "
    ProxyRequests on
    ProxyVia block
    AllowCONNECT 22 996
    # Proxy: Deny all proxying by default
    <Proxy *>                      Require all denied  </Proxy>

    # but enable the following
    <Proxy 127.0.0.3>              Require all granted  </Proxy>
    <Proxy tritux>                 Require all granted  </Proxy>
"

# proxytunnel -p 192.168.18.9:80 -d 127.0.0.3:22 -v
# proxytunnel -p 192.168.18.9:80 -d tritux:996 -v
}
