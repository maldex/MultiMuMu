# figure container name
pwd=`pwd`
name=${pwd##*/}
echo "build `date +%Y%m%d-%H%M` of ${name} by `whoami`@`hostname`" | tee build.out
time docker build -t my_dvb_toolbox . 2>&1 | tee -a build.out
docker run -it --rm --device /dev/dvb/ my_dvb_toolbox mumudvb -l
docker images my_dvb_toolbox
