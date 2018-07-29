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
RUN     dnf install -y wget tar xz gzip git gcc gcc-c++ make libev libev-devel xz elfutils-libelf-devel mercurial perl-Proc-ProcessTable kernel-devel kernel-headers automake autoconf dh-autoreconf v4l-utils glibc-static libstdc++-static
#RUN     dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

 
# do not use pre-built dvb-apps from distro-mirror, but build from sources. This is required for MuMuDVB's CAM support on fedora.
RUN     cd /usr/local/src && \
        hg clone http://linuxtv.org/hg/dvb-apps && \
        cd dvb-apps && \
        # patching for >=4.14 Kernel (https://aur.archlinux.org/packages/linuxtv-dvb-apps)
        wget -q -O - https://git.busybox.net/buildroot/plain/package/dvb-apps/0003-handle-static-shared-only-build.patch | patch -p1 && \
        wget -q -O - https://git.busybox.net/buildroot/plain/package/dvb-apps/0005-utils-fix-build-with-kernel-headers-4.14.patch | patch -p1 && \
        wget -q -O - https://gitweb.gentoo.org/repo/gentoo.git/plain/media-tv/linuxtv-dvb-apps/files/linuxtv-dvb-apps-1.1.1.20100223-perl526.patch | patch -p1 && \
        make && make install && \
        ldconfig   # b/c libdvben50221.so
 
RUN     cd /usr/local/src && \
        git clone git://git.videolan.org/bitstream.git && \
        cd bitstream && \
        make all && make install
		
RUN		cd /usr/local/src && \
		git clone https://code.videolan.org/videolan/libdvbcsa.git && \
		cd libdvbcsa && \
		autoreconf -i -f && \
		./configure --prefix=/usr && make && make install

####### OSCAM SUPPORT ####### 
RUN     yum install -y openssl openssl-devel dialog svn pcsc-lite pcsc-lite-devel libusb libusb-devel
		
RUN		cd /usr/local/src && \
		svn checkout http://www.streamboard.tv/svn/oscam/trunk oscam-svn && \
		cd oscam-svn && \
		make USE_PCSC=1 USE_LIBUSB=1
         
RUN		cd /usr/local/src && \
		git clone https://github.com/gfto/tsdecrypt.git && \
		cd tsdecrypt && \
		git submodule init && \
		git submodule update && \
		make && make install
############################# 
		
RUN     cd /usr/local/src && \
        git clone https://code.videolan.org/videolan/dvblast.git && \
        cd dvblast && \
        make all && make install
         
RUN     cd /usr/local/src && \
        wget http://wirbel.htpc-forum.de/w_scan/w_scan-20170107.tar.bz2 && \
        tar -jxf w_scan-20170107.tar.bz2 && \
        cd w_scan-20170107/ && \
        ./configure && make && make install
          
RUN     cd /usr/local/src && \
        git clone https://github.com/stefantalpalaru/w_scan2.git && \
        cd w_scan2 && \
        autoreconf -i -f && \
        ./configure && make && make install
         
RUN     cd /usr/local/src && \
        wget http://udpxy.com/download/udpxy/udpxy-src.tar.gz && \
        tar -zxf udpxy-src.tar.gz && \
        cd udpxy-*/ && \
        make && make install
          
RUN     cd /usr/local/src && \
        wget ftp://ftp.videolan.org/pub/videolan/miniSAPserver/0.3.8/minisapserver-0.3.8.tar.xz && \
        tar -Jxf minisapserver-0.3.8.tar.xz && \
        cd minisapserver-*/ && \
        ./configure && make && make install
			
RUN		cd /usr/local/src && \
		ldconfig && \
        git clone https://github.com/braice/MuMuDVB.git && \
        cd MuMuDVB && \
        autoreconf -i -f && \
        ./configure --enable-cam-support --enable-scam-support --enable-android && \
        make && make install
		
###
# Part 2: install but not compile the applications. This leads to a much smaller image
###
FROM    fedora:28
RUN     echo "############################# RUNTIME IMAGE #################################"
 
# copy the whole /usr/local from the previous compiler-image (note the --from)
COPY    --from=compiler_build /usr/local /usr/local
 
# install runtime libraries
RUN     dnf install -y v4l-utils libev openssl openssl-devel pcsc-lite libusb
 
# unfortunately, some make's need gcc anyway :(
RUN     dnf install -y make gcc gcc-c++ cpp glibc-devel glibc-headers kernel-headers
 
RUN     cd /usr/local/src/dvb-apps && make install && ldconfig
RUN     cd /usr/local/src/libdvbcsa && make install && ldconfig
RUN		cd /usr/local/src/tsdecrypt && make install
RUN     cd /usr/local/src/bitstream && make install
RUN     cd /usr/local/src/dvblast && make install
RUN     cd /usr/local/src/w_scan-20170107 && make install
RUN     cd /usr/local/src/w_scan2 && make install
RUN     cd /usr/local/src/udpxy-*/ && make install
RUN     cd /usr/local/src/minisapserver-*/ && make install
RUN     cd /usr/local/src/MuMuDVB && ldconfig && make install
 
# remove gcc again
RUN     dnf remove -y make gcc gcc-c++ cpp glibc-devel glibc-headers kernel-headers
 
# add a runtime user
RUN     useradd -c "simple user" -g users -G audio,video,cdrom,dialout,lp,tty,games user
 
# include this very file into the image
COPY    Dockerfile /
COPY    build.out /
 
# use this user as default user
USER    user
 
# assume persistent storage
VOLUME  /conf
 
# assume exposed ports
EXPOSE  8500:8500
 
# assume standard runtime executable
CMD     ["/bin/bash"]
 
###
# Part 3: build, verify and use this image
###
# build the container
# $ time docker build -t my_dvb_toolbox .
 
# explore the container. default bash is defined by CMD in dockerfile
# $ docker run -it --rm my_dvb_toolbox
 
# run a scan. note the mapped device tree /dev/dvb
# $ docker run -it --rm --device /dev/dvb/ my_dvb_toolbox w_scan -f s -s S13E0 -D1c
 
# run a mumudvb instance. Note the mapped device, filesystem and tcp-port
# $ docker run -it --rm --device /dev/dvb/ --volume ${PWD}/conf:/conf -p 8500:8500 my_dvb_toolbox mumudvb -d -c /conf/test.conf
