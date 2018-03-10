#!/usr/bin/env bash

# --------------------------
# Install jenkins
# NEED GPG KEY
# --------------------------

# wget -q -O - http://pkg.jenkins-ci.org/debian-stable/jenkins-ci.org.key | apt-key add
# echo "deb http://pkg.jenkins-ci.org/debian-stable binary/" > /etc/apt/sources.list.d/jenkins.list
# apt update
# apt install jenkins
# cat /var/lib/jenkins/secrets/initialAdminPassword

# echo "Got to http://jenkins-server-IP:8080"
# echo "Got to http://jenkins-server-IP:8080"
# echo "Got to http://jenkins-server-IP:8080"

# --------------------------
# Python 2.7.13
# --------------------------

# Need sudo
if [[ $UID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

apt-get install -y virtualenvwrapper
apt-get install -y zlib1g-dev libssl-dev libbz2-dev xz-utils wget
apt-get install -y dh-systemd dh-virtualenv

echo "===================================="
echo "CLEAN"
echo "===================================="
rm -rf /tmp/py2713

echo "===================================="
echo "DOWNLOAD"
echo "===================================="

curl https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz -o /tmp/Python-2.7.13.tgz

echo "===================================="
echo "DECOMPRESS"
echo "===================================="

mkdir /tmp/py2713
tar zxf /tmp/Python-2.7.13.tgz -C /tmp/py2713

echo "===================================="
echo "PREPARE"
echo "===================================="
rm -rf '/opt/Python-2.7.13'
mkdir -p '/opt/Python-2.7.13'

echo "===================================="
echo "MAKE /opt/Python-2.7.13"
echo "===================================="

echo "Update setup, we need SSL support, so we ack Modules/Setup"
set -e
pwd
cp -f Setup.dist /tmp/py2713/Python-2.7.13/Modules/Setup.dist
grep SSL /tmp/py2713/Python-2.7.13/Modules/Setup.dist
set +e

echo "Fire"
cd /tmp/py2713/Python-2.7.13
./configure --prefix="/opt/Python-2.7.13" --enable-optimizations
make -j4
make install

echo "===================================="
echo "CHECK"
echo "===================================="
/opt/Python-2.7.13/bin/python2.7 --version




