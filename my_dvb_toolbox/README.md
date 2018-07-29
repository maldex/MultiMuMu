```
cat <<EOF > /etc/yum.repos.d/docker.repo
[dockerrepo]
name=Docker Repository
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
#baseurl=https://yum.dockerproject.org/repo/main/centos/7/
baseurl=https://yum.dockerproject.org/repo/main/fedora/25/
EOF
 
yum install -y docker-engine git make python-pip
pip install --upgrade pip; pip install docker-compose
 
usermod -a -G docker user
  
# local engine: enable docker
systemctl enable docker; systemctl start docker
```