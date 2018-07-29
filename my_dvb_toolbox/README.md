see https://hub.docker.com/r/maldex/my_dvb_toolbox/

## Install Docker
```
# add docker repo for redhat systems
cat <<EOF > /etc/yum.repos.d/docker.repo
[dockerrepo]
name=Docker Repository
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
#baseurl=https://yum.dockerproject.org/repo/main/centos/7/
baseurl=https://yum.dockerproject.org/repo/main/fedora/25/
EOF
 
# install the engine
yum install -y docker-engine 

# local engine: enable and start docker-engine
systemctl enable docker; systemctl start docker

# enable your local user to execute docker 
usermod -a -G docker user
```

## pull image and sample config
```
docker pull maldex/my_dvb_toolbox
docker inspect maldex/my_dvb_toolbox

wget -O /tmp/mumu.conf https://raw.githubusercontent.com/maldex/MultiMuMu/master/my_dvb_toolbox/mumudvb-s.conf
```

h2. try n run
```
# check if your dvb might work
docker run -it --rm --device /dev/dvb/ maldex/my_dvb_toolbox mumudvb -l

# give it a shot on port 8500
docker run -it --rm --device /dev/dvb/ --volume /tmp:/tmp -p 8500:8500 maldex/my_dvb_toolbox mumudvb -d -c /tmp/mumu.conf
```



