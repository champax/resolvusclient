#!/usr/bin/env bash

# ========================================================
# ========================================================
# CRITICAL FOR CENTOS
# ========================================================
# ========================================================
# NEVER NEVER NEVER configure with the flag "--enable-shared"
# This may/will cause the "/usr/lib64/libpython2.7.so.1.0" to be overriden (system wide if you are not lucky)
# Doing this, the system python will upgrade to 2.7.13 or newer
# And this basterd of yum will die (not recoverable i assume)
# SO : We build/link without generating the shared library
# SO : We can have 2 version of python running, the pre-paleolithic 2.7.5 and the newer 2.7.13
# ========================================================
# ========================================================

# Need sudo
if [[ $UID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Stuff required for build (we need python compiled with zlib and ssl embedded for https)
yum install -y python-virtualenvwrapper
yum install -y zlib-devel
yum install -y openssl openssl-devel zlib-devel bzip2-devel xz-libs wget
yum install -y rpm-build

# PYTHON (what a huge huge mess to recompile python 2.7 for this poor linux distro which just run a 2.7.5, just 4.5 years old)
# https://github.com/opena11y/fae2/blob/master/python27.md
# https://stackoverflow.com/questions/5937337/building-python-with-ssl-support-in-non-standard-location
# https://stackoverflow.com/questions/6169522/no-module-named-zlib
# https://stackoverflow.com/questions/29486113/problems-with-python-and-virtualenvwrapper-after-updating-no-module-named-virtu
# https://stackoverflow.com/questions/1534210/use-different-python-version-with-virtualenv/39713544#39713544

# DIRS
PY_2713_DIR=/opt/Python-2.7.13

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
rm -rf ${PY_2713_DIR}
mkdir -p ${PY_2713_DIR}

echo "===================================="
echo "MAKE ${PY_2713_DIR}"
echo "===================================="

echo "Update setup (we need SSL support, so we ack Modules/Setup"
set -e
pwd
cp -f Setup.txt /tmp/py2713/Python-2.7.13/Modules/Setup
grep SSL /tmp/py2713/Python-2.7.13/Modules/Setup
set +e

echo "Fire"
cd /tmp/py2713/Python-2.7.13
./configure --prefix="${PY_2713_DIR}" --enable-optimizations
make -j4
make install

echo "===================================="
echo "CHECK"
echo "===================================="
${PY_2713_DIR}/bin/python2.7 --version
