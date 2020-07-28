h2. based on CentOS 8

export pUser=MultiMuMu

function clone_project() {
    if ! getent passwd ${pUser}; then
        useradd -c "MultiMuMu project user" -g users -G tty,dialout,video,audio,sudoers ${pUser}
        echo "${pUser}-${pUser}" | passwd ${pUser} --stdin
        su - ${pUser} -c "`which ssh-keygen` -q -N '' -f ~/.ssh/id_rsa -C ${pUser}@`hostname -f`-`date +%Y%m%d-%H%M`"
        su - ${pUser} -c "ssh-keyscan github.com >> ~/.ssh/known_hosts"
        echo " ---"
        cat `getent passwd ${pUser} | cut -d: -f 6`/.ssh/id_rsa.pub
        echo " ---"
    fi
    dnf install -y git
    su - ${pUser} -c "git clone git@github.com:maldex/MultiMuMu.git"
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

function build_mumudvb_container() {
    pushd `getent passwd ${pUser} | cut -d: -f 6`/MultiMuMu/Docker > /dev/null
    sed -r 's_^#(cam|scam|tool);__g' Dockerfile | docker build -t mumudvb:sak    . -f -
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

function build_docker() {
}