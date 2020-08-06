h2. based on CentOS 8

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
}

function build_mumudvb_container() {
    su - ${pUser} -c "cd ~/MultiMuMu/Docker; sed -r 's_^#(cam|scam|tool);__g' Dockerfile.MumuDVB | docker build -t mumudvb:sak . -f -"
}

function install_docker() {
    echo "    ${FUNCNAME[*]} >> installing Docker"
    dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
        
    yum install --nobest -y docker-ce
    systemctl enable --now docker
    
    firewall-cmd --permanent --zone=trusted --add-interface=docker0
    firewall-cmd --reload
    
    # add all users that belong to users also to docker
    for u in `getent group users | awk -F':' '{print $NF}' | tr ',' ' '`; do
        echo "    ${FUNCNAME[*]} >> adding user '${u}' to group 'docker'"
        usermod -a -G docker ${u}
    done
    
    composeVersion=1.26.0
    echo "    ${FUNCNAME[*]} >> downloading docker-compose ${composeVersion} for $(uname -s) $(uname -m)"
    curl -L "https://github.com/docker/compose/releases/download/${composeVersion}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/bin/docker-compose
    chmod -v +x /usr/bin/docker-compose
}

function clone_project() {
    if ! getent passwd ${pUser}; then
        useradd -c "MultiMuMu project user" -g users -G tty,dialout,video,audio,sudoers ${pUser}
        echo "${pUser}-${pUser}" | passwd ${pUser} --stdin
        su - ${pUser} -c "`which ssh-keygen` -q -N '' -f ~/.ssh/id_rsa -C ${pUser}@`hostname -f`-`date +%Y%m%d-%H%M`"
        su - ${pUser} -c "cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys"
        su - ${pUser} -c "ssh-keyscan github.com >> ~/.ssh/known_hosts"
        echo " ---"
        cat `getent passwd ${pUser} | cut -d: -f 6`/.ssh/id_rsa.pub
        echo " ---"
    fi
    dnf install -y git
    su - ${pUser} -c "git clone git@github.com:maldex/MultiMuMu.git"
    }


function build_mumudvb_container() {
    pushd `getent passwd ${pUser} | cut -d: -f 6`/MultiMuMu/Docker > /dev/null
    sed -r 's_^#(cam|scam|tool);__g' Dockerfile.MumuDVB | docker build -t mumudvb:sak . -f -
    cat Dockerfile.MultiMuMu | docker build -t multimumu:latest . -f -
    popd > /dev/null
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
    echo "it's recommended to reboot now"
}

clone_project
install_ddriver_requirements
install_ddriver
install_docker
build_mumudvb_container

install_service_frontail
