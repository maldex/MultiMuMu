# sample setup against a CentOS(7)/Fedora(25)
## some handy yum packets
```
yum install wget mc iptraf-ng
# if CentOS: yum -y install http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
yum install -y w_scan
yum install -y vlc dvb-apps
```

## devel stuff
```
yum install -y git gcc gcc-c++ make libev libev-devel xz libdvbcsa-devel
yum install -y mercurial perl-Proc-ProcessTable kernel-devel kernel-headers automake autoconf dh-autoreconf
cd /usr/local/src
```

## install DigitalDevices Kernel Driver (if you own such hardware)
```
wget https://github.com/DigitalDevices/dddvb/archive/0.9.29.tar.gz
tar -zxf 0.9.*.tar.gz
cd dddvb-0.9.*/
make && make install
echo "search extra updates built-in" > /etc/depmod.d/extra.conf
echo "options ddbridge adapter_alloc=3" > /lib/modprobe.d/ddbridge.conf
echo "options dvb-core cam_debug=1" >> /lib/modprobe.d/ddbridge.conf
#options dvb-core cam_debug=1,1 debug=1,1
depmod -a
modprobe ddbridge
dmesg | grep -i ddbridge
# reboot
```

## install MuMuDVB
```
git clone https://github.com/braice/MuMuDVB.git
pushd MuMuDVB
autoreconf -i -f
./configure --disable-cam-support --enable-scam-support --enable-android
make && make install
popd
```

### install some other stuff
```
cd /usr/local/src
git clone git://git.videolan.org/bitstream.git
pushd bitstream
make all && make install
popd
 
wget https://get.videolan.org/dvblast/3.0/dvblast-3.0.tar.bz2
tar -jxvf dvblast-*.tar.bz2
pushd dvblast-*
make all && make install
popd
 
wget http://www.udpxy.com/download/1_23/udpxy.1.0.23-9-prod.tar.gz
tar -zxvf udpxy.1.0.23-9-prod.tar.gz
pushd udpxy-1.0.23-9
make && make install
popd
 
wget ftp://ftp.videolan.org/pub/videolan/miniSAPserver/0.3.8/minisapserver-0.3.8.tar.xz
xz -d minisapserver-0.3.8.tar.xz
tar -xvf minisapserver-0.3.8.tar
pushd minisapserver-0.3.8
./configure && make && make install
popd
```
## experimental: CAM support
```
yum install -y openssl-devel dialog
cd /usr/local/src
 
wget https://download.videolan.org/videolan/libdvbcsa/1.1.0/libdvbcsa-1.1.0.tar.gz
tar -zxf libdvbcsa-1.1.0.tar.gz
pushd libdvbcsa-1.1.0/
./configure --prefix=/usr --enable-static
make all && make install
popd
 
svn checkout http://www.streamboard.tv/svn/oscam/trunk@11086 oscam-11086
pushd oscam-11086/
wget -O - https://raw.githubusercontent.com/oscam-emu/oscam-emu/master/oscam-emu.patch | patch -p0
#make config
make
cp Distribution/oscam-*stable_svn11086-*-linux /usr/local/bin/oscam
echo "[account]
user     = user
pwd      = pass
group    = 1
au       = 1
uniq     = 0
monlevel = 4" >> /usr/local/etc/oscam.user
popd
 
git clone https://github.com/gfto/tsdecrypt.git
pushd tsdecrypt
git submodule init
git submodule update
make && make install
popd
```
