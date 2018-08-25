# try'n'error dockerfile (>=17.05) for mumudvb, dvblast and other headless TV applications
# mkdir my_dvb_toolbox; cd my_dvb_toolbox; vi Dockerfile
 
###
# Part 1: install compilers and devel-utils, download and build applications
###
 
# start from a fedora 28 image
FROM    fedora:28 AS compiler_build
RUN     echo "############################# COMPILER IMAGE #################################"
  
# install requirements
#RUN     dnf upgrade -y && dnf clean all
RUN     dnf install -y git gcc gcc-c++ make automake autoconf gettext-devel

#RUN     dnf install -y tar xz elfutils-libelf-devel  perl-Proc-ProcessTable kernel-devel kernel-headers dh-autoreconf v4l-utils glibc-static libstdc++-static 

#######
#  OPTIONAL: CAM SUPPORT 
#######
#cam;RUN     dnf install -y wget mercurial patch glibc-static
#cam;
#cam;# do not use pre-built dvb-apps and libdvbcsa from distro-mirror, but build from sources. This is required for cam support on fedora.
#cam;RUN     cd /usr/local/src && \
#cam;        hg clone http://linuxtv.org/hg/dvb-apps && \
#cam;        cd dvb-apps && \
#cam;        # patching for >=4.14 Kernel (https://aur.archlinux.org/packages/linuxtv-dvb-apps)
#cam;        wget -q -O - https://git.busybox.net/buildroot/plain/package/dvb-apps/0003-handle-static-shared-only-build.patch | patch -p1 && \
#cam;        wget -q -O - https://git.busybox.net/buildroot/plain/package/dvb-apps/0005-utils-fix-build-with-kernel-headers-4.14.patch | patch -p1 && \
#cam;        wget -q -O - https://gitweb.gentoo.org/repo/gentoo.git/plain/media-tv/linuxtv-dvb-apps/files/linuxtv-dvb-apps-1.1.1.20100223-perl526.patch | patch -p1 && \
#cam;        make && make install && \
#cam;        ldconfig   # b/c libdvben50221.so

#######
# OPTIONAL: SCAM SUPPORT 
#######
#scam;RUN     yum install -y openssl-devel dialog svn pcsc-lite pcsc-lite-devel libusb libusb-devel findutils file libtool
#scam;
#scam;RUN     cd /usr/local/src && \
#scam;        git clone https://code.videolan.org/videolan/libdvbcsa.git && \
#scam;        cd libdvbcsa && \
#scam;        autoreconf -i -f && \
#scam;        ./configure --prefix=/usr && make && make install && \
#scam;		ldconfig   # b/c libdvbcsa.so
#scam;        #dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm && \
#scam;        #dnf install -y libdvbcsa-devel
#scam;
#scam;RUN     cd /usr/local/src && \
#scam;        svn checkout http://www.streamboard.tv/svn/oscam/trunk oscam-svn && \
#scam;        cd oscam-svn && \
#scam;        make USE_PCSC=1 USE_LIBUSB=1
#scam;         
#scam;RUN     cd /usr/local/src && \
#scam;        git clone https://github.com/gfto/tsdecrypt.git && \
#scam;        cd tsdecrypt && \
#scam;        git submodule init && \
#scam;        git submodule update && \
#scam;        make && make install    
     
#######	 
# REQUIRED: ACTUAL APPLICATION ITSELF
#######
# note: the ./configure will detect cam/scam support automagically if everything provided
RUN     cd /usr/local/src && \
        ldconfig && \
        git clone https://github.com/braice/MuMuDVB.git && \
        cd MuMuDVB && \
        autoreconf -i -f && \
        ./configure --enable-android && \
        make && make install

#######
# OPTIONAL: TOOLBOXING
####### 
#tool;RUN     cd /usr/local/src && \
#tool;        git clone git://git.videolan.org/bitstream.git && \
#tool;        cd bitstream && \
#tool;        make all && make install
#tool;
#tool;RUN     cd /usr/local/src && \
#tool;		dnf install -y libev-devel && \
#tool;        git clone https://code.videolan.org/videolan/dvblast.git && \
#tool;        cd dvblast && \
#tool;        make all && make install
#tool;         
#tool;RUN     cd /usr/local/src && \
#tool;        yum install -y wget bzip2 && \
#tool;        wget http://wirbel.htpc-forum.de/w_scan/w_scan-20170107.tar.bz2 && \
#tool;        tar -jxf w_scan-20170107.tar.bz2 && \
#tool;        cd w_scan-20170107/ && \
#tool;        ./configure && make && make install
#tool;          
#tool;RUN     cd /usr/local/src && \
#tool;        git clone https://github.com/stefantalpalaru/w_scan2.git && \
#tool;        cd w_scan2 && \
#tool;        autoreconf -i -f && \
#tool;        ./configure && make && make install
#tool;         
#tool;RUN     cd /usr/local/src && \
#tool;		yum install -y wget && \
#tool;        wget http://udpxy.com/download/udpxy/udpxy-src.tar.gz && \
#tool;        tar -zxf udpxy-src.tar.gz && \
#tool;        cd udpxy-*/ && \
#tool;        make && make install 
#tool;          
#tool;RUN     cd /usr/local/src && \
#tool;        yum install -y xz wget && \
#tool;        wget ftp://ftp.videolan.org/pub/videolan/miniSAPserver/0.3.8/minisapserver-0.3.8.tar.xz && \
#tool;        tar -Jxf minisapserver-0.3.8.tar.xz && \
#tool;        cd minisapserver-*/ && \
#tool;        ./configure && make && make install
#tool;
#tool;RUN		/bin/false
        
###
# Part 2: install but not compile the applications. This leads to a much smaller image
###
FROM    fedora:28
RUN     echo "############################# RUNTIME IMAGE #################################"
 
# copy the whole /usr/local from the previous compiler-image (note the --from)
COPY    --from=compiler_build /usr/local /usr/local
 
# install runtime libraries - not t-shirt sized ... :/
RUN     dnf install -y v4l-utils libev openssl-devel pcsc-lite libusb
 
# unfortunately, some make's need gcc anyway :(
RUN     dnf install -y make gcc gcc-c++ cpp glibc-devel glibc-headers kernel-headers
 
RUN     test -e /usr/local/src/dvb-apps && cd /usr/local/src/dvb-apps && make install && ldconfig
RUN     test -e /usr/local/src/libdvbcsa && cd /usr/local/src/libdvbcsa && make install && ldconfig
RUN     test -e /usr/local/src/MuMuDVB && cd /usr/local/src/MuMuDVB && make install
RUN     test -e /usr/local/src/tsdecrypt && cd /usr/local/src/tsdecrypt && make install
RUN     test -e /usr/local/src/bitstream && cd /usr/local/src/bitstream && make install
RUN     test -e /usr/local/src/dvblast && cd /usr/local/src/dvblast && make install
RUN     test -e /usr/local/src/w_scan-20170107 && cd /usr/local/src/w_scan-20170107 && make install
RUN     test -e /usr/local/src/w_scan2 && cd /usr/local/src/w_scan2 && make install
RUN     test -e /usr/local/src/udpxy-*/ && cd /usr/local/src/udpxy-*/ && make install
RUN     test -e /usr/local/src/minisapserver-*/ && cd /usr/local/src/minisapserver-*/ && make install

 
# remove gcc again
RUN     dnf remove -y make gcc gcc-c++ cpp glibc-devel glibc-headers kernel-headers
 
# add a runtime user
RUN     useradd -c "simple user" -g users -G audio,video,cdrom,dialout,lp,tty,games user
 
# include this very file into the image
COPY    Dockerfile /
 
# use this user as default user
USER    user
 
# assume persistent storage
VOLUME  /tmp
 
# assume exposed ports
EXPOSE  8500:8500
 
# assume standard runtime executable
CMD     ["/bin/bash"]
 
###
# Part 3: build, verify and use this image
###
# build the container
# $ c
 
# explore the container. default bash is defined by CMD in dockerfile
# $ docker run -it --rm my_dvb_toolbox
 
# run a scan. note the mapped device tree /dev/dvb
# $ docker run -it --rm --device /dev/dvb/ my_dvb_toolbox w_scan -f s -s S13E0 -D1c
 
# run a mumudvb instance. Note the mapped device, filesystem and tcp-port
# $ docker run -it --rm --device /dev/dvb/ --volume ${PWD}/conf:/conf -p 8500:8500 my_dvb_toolbox mumudvb -d -c /conf/test.conf
