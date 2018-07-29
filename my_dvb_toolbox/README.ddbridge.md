Install ddbridge-driver for Digital Devices [Cine S2 V6.5](https://digitaldevices.de/products/dvb_components/cine_s2) and [DuoFlex CI](https://digitaldevices.de/products/dvb_components/duoflex_ci) on redhat flavour.

```
dnf install -y kernel-headers-`uname -r` kernel-devel-`uname -r` elfutils-libelf-devel git gcc gcc-c++ make usbutils
 
rmmod ddbridge dvb_core cxd2099
cd /usr/local/src
git clone https://github.com/DigitalDevices/dddvb.git
pushd dddvb
make && make install
echo "search extra updates built-in" > /etc/depmod.d/extra.conf
echo "options ddbridge adapter_alloc=3" > /lib/modprobe.d/ddbridge.conf
echo "options dvb_core debug=0 cam_debug=1" >>  /lib/modprobe.d/ddbridge.conf
depmod -a
modprobe ddbridge
dmesg
# reboot
popd
 
# about TAB/CAM:  https://www.spinics.net/lists/linux-media/msg39494.html     http://mumudvb.net/documentation/asciidoc/mumudvb-2.0.0/README.html#_hardware_cam_issues
# wire: Tuner0 -> Input0 -> Port0 (TAB1, DVB-S2) ==>  Port2(TAB3, CAM1)
# wire: Tuner0 -> Input1 -> Port0 (TAB1, DVB-S2) ==>  Port3(TAB4, CAM2)
 
sudo rmmod ddbridge dvb_core cxd2099; sudo modprobe ddbridge
echo "00 02" | sudo tee /sys/class/ddbridge/ddbridge0/redirect
echo "01 03" | sudo tee /sys/class/ddbridge/ddbridge0/redirect
```

```
Monoblock LNB, Astra & Hotbird
   | | | |  
   | | | |    
   | | | |  
 +---------+
 |         |
 | DiSEqC  |   (EXR2908)
 |         |
 +---------+
   |     | 
   |     | 
   |     |   |
-------------+
  |         |
  | C     |||  TAB4 -> CI TAB1 with TechniSat CAM and SRF Access Card
  | i     |||
--+ n       |
|   e     |||  TAB3 -> CI TAB1 with TechniSat CAM and SRF Access Card
|         |||
|   S       |
--+ 6     |||  TAB2 ->  empty
  | .     |||
  | 5       |
  +---------+
```