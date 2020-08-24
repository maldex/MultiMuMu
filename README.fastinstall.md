intel me: http://ip:16992/
### based on CentOS 8
```
export pUser=MultiMuMu

function install_service_frontail(){
    echo "  >> adding FRONTAIL"
    dnf install -y npm
    npm install frontail -g

    cat << EOF > /usr/lib/systemd/system/frontail.service
[Unit]
Description=Frontail log2web
 
[Service]
ExecStart=/usr/local/bin/frontail -p 7411 --ui-highlight -t dark /var/log/httpd/access_log /var/log/httpd/error_log /home/MultiMuMu/MultiMuMu/MultiMuMu.log
 
[Install]
WantedBy=multi-user.target
EOF

    firewall-cmd --permanent --add-port=7411/tcp
    firewall-cmd --reload
    systemctl daemon-reload
    systemctl enable --now frontail
}



function install_apache(){
    source `getent passwd ${pUser} | cut -d: -f 6`/MultiMuMu/Docker/apache.functions.sh
    apache_install_all
    apache_minimum_modules 
    apache_enable_proxy
    apache_enable_balancer
    mv /etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf.org
    cp `getent passwd ${pUser} | cut -d: -f 6`/MultiMuMu/Docker/httpd.conf /etc/httpd/conf/httpd
    chown root:apache /MultiMuMu/Docker/httpd.conf

mkdir ~apache/.ssh
vi ~apache/.ssh/id_rsa
chown -R apache:apache ~apache/.ssh
chmod 700 ~apache/.ssh; chmod 600 ~apache/.ssh/id_rsa
usermod -s /bin/bash apache
su - apache
ssh MultiMuMu@DVB-S0  # no passwd!
ssh MultiMuMu@DVB-S1  # no passwd!
usermod -s /bin/nologin apache
}


function project_requs() {
    dnf install -y git
    dnf install -y findutils git python3-pip wget acl python3
    pip3 install simplejson xmltodict paramiko
    cat <<EOF >> /etc/hosts
127.0.0.1   DVB-S0  DVB-S1 frontail
EOF



}

function clone_project() {
    if ! getent passwd ${pUser}; then
        useradd -c "MultiMuMu project user" -g users -G tty,dialout,video,audio,sudoers ${pUser}
        echo "${pUser}-${pUser}" | passwd ${pUser} --stdin
        su - ${pUser} -c "`which ssh-keygen` -q -N '' -f ~/.ssh/id_rsa -C ${pUser}@`hostname -s`-`date +%Y%m%d-%H%M`"
        su - ${pUser} -c "cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys"
        su - ${pUser} -c "ssh-keyscan github.com >> ~/.ssh/known_hosts"
        echo " ---"
        cat `getent passwd ${pUser} | cut -d: -f 6`/.ssh/id_rsa.pub
        echo " ---"
    fi
    su - ${pUser} -c "git clone git@github.com:maldex/MultiMuMu.git"
    }

function install_ddriver_requirements() {
    dnf install -y git gcc gcc-c++ make libev libev-devel xz libdvbcsa-devel elfutils-libelf-devel openssl-devel dkms
    dnf install -y mercurial perl-Proc-ProcessTable kernel-devel kernel-headers automake autoconf dh-autoreconf 
}

function install_ddriver() {
    cd /usr/local/src
    sudo wget -qO - https://github.com/DigitalDevices/dddvb/archive/0.9.37.tar.gz | tar zxvf -
    cd dddvb-0.9.*/
    make && sudo make install
    echo "search extra updates built-in" | sudo tee etc/depmod.d/extra.conf
    echo "options ddbridge adapter_alloc=3" | sudo tee /lib/modprobe.d/ddbridge.conf
    echo "options dvb-core cam_debug=1" | sudo tee -a /lib/modprobe.d/ddbridge.conf
    #options dvb-core cam_debug=1,1 debug=1,1
    sudo depmod -a
    sudo rmmod ddbridge; sudo modprobe ddbridge
    dmesg | grep -i -e ddbridge -e dvb_ca
    echo "rmmod ddbridge ; modprobe -v ddbridge; echo \"00 02\" > /sys/class/ddbridge/ddbridge0/redirect" >> /etc/rc.local
    echo "it's recommended to reboot now"

}

function install_mumudvb(){
	dnf install -y git gcc gcc-c++ make automake autoconf gettext-devel wget mercurial patch glibc-static openssl-devel dialog svn pcsc-lite pcsc-lite-devel libusb libusb-devel findutils file libtool libev-devel

#######
# requirements
####### 

	# do not use pre-built dvb-apps and libdvbcsa from distro-mirror, but build from sources. This is required for cam support on fedora.
	cd /usr/local/src && \
        hg clone http://linuxtv.org/hg/dvb-apps && \
        cd dvb-apps && \
        # patching for >=4.14 Kernel (https://aur.archlinux.org/packages/linuxtv-dvb-apps)
        wget -q -O - https://git.busybox.net/buildroot/plain/package/dvb-apps/0003-handle-static-shared-only-build.patch | patch -p1 && \
        wget -q -O - https://git.busybox.net/buildroot/plain/package/dvb-apps/0005-utils-fix-build-with-kernel-headers-4.14.patch | patch -p1 && \
        wget -q -O - https://gitweb.gentoo.org/repo/gentoo.git/plain/media-tv/linuxtv-dvb-apps/files/linuxtv-dvb-apps-1.1.1.20100223-perl526.patch | patch -p1 && \
        make && make install && \
        ldconfig   # b/c libdvben50221.so

	cd /usr/local/src && \
        git clone https://code.videolan.org/videolan/libdvbcsa.git && \
        cd libdvbcsa && \
        autoreconf -i -f && \
        ./configure --prefix=/usr && make && make install && \
	ldconfig   # b/c libdvbcsa.so

	cd /usr/local/src && \
        svn checkout http://www.streamboard.tv/svn/oscam/trunk oscam-svn && \
        cd oscam-svn && \
        make USE_PCSC=1 USE_LIBUSB=1

	cd /usr/local/src && \
        git clone https://github.com/gfto/tsdecrypt.git && \
        cd tsdecrypt && \
        git submodule init && \
        git submodule update && \
        make && make install    

#######
# MUMUDVB
####### 
# note: the ./configure will detect cam/scam support automagically if everything provided
	cd /usr/local/src && \
        ldconfig && \
        git clone https://github.com/braice/MuMuDVB.git && \
        cd MuMuDVB && \
        autoreconf -i -f && \
        ./configure --enable-android && \
        make && make install

#######
# OPTIONAL: TOOLBOXING
####### 
     cd /usr/local/src && \
        git clone https://code.videolan.org/videolan/bitstream.git && \
        cd bitstream && \
        make all && make install

    cd /usr/local/src && \
        git clone https://code.videolan.org/videolan/dvblast.git && \
        cd dvblast && \
        make all && make install
         
     cd /usr/local/src && \
        git clone https://github.com/Max-T/w_scan.git&& \
        cd w_scan/ && \
        sh ./configure && make && make install
          
     cd /usr/local/src && \
        git clone https://github.com/stefantalpalaru/w_scan2.git && \
        cd w_scan2 && \
        autoreconf -i -f && \
        ./configure && make && make install
         
     cd /usr/local/src && \
	yum install -y wget && \
        wget http://udpxy.com/download/udpxy/udpxy-src.tar.gz && \
        tar -zxf udpxy-src.tar.gz && \
        cd udpxy-*/ && \
        make && make install 
          
     cd /usr/local/src && \
        yum install -y xz wget && \
        wget ftp://ftp.videolan.org/pub/videolan/miniSAPserver/0.3.8/minisapserver-0.3.8.tar.xz && \
        tar -Jxf minisapserver-0.3.8.tar.xz && \
        cd minisapserver-*/ && \
        ./configure && make && make install
}

function prepare_http(){
	yum install -y https://pkgs.dyn.su/el8/extras/x86_64/mod_evasive-1.10.1-33.el8.x86_64.rpm
	cd ~MultiMuMu/MultiMuMu/Docker/
	source apache.functions.sh
	apache_install_all && \
	apache_minimum_modules  && \
	apache_default_vhost  && \
	apache_lil_tweaks  && \
	apache_enable_proxy  && \
	apache_enable_balancer

cd /etc/httpd/conf
cp -v ~MultiMuMu/MultiMuMu/Docker/httpd.conf ./
chown root:apache httpd.conf
httpd -S
setfacl -R -d -m u:apache:rX ~MultiMuMu/
setfacl -R -m u:apache:rX ~MultiMuMu/

setfacl -R -d -m u:apache:rwX ~MultiMuMu/MultiMuMu/log
setfacl -R -m u:apache:rwX ~MultiMuMu/MultiMuMu/log

}

clone_project
install_ddriver_requirements
install_ddriver
install_docker



install_service_frontail
```


```
docker-compose down
docker-compose up --build
docker-compose up
