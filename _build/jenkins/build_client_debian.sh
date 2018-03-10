#!/bin/bash -e

echo "=========================="
echo "build_client_debian.sh called"
echo "=========================="

echo "=========================="
echo "Init"
echo "=========================="

# Debian :
# /usr/share/virtualenvwrapper/virtualenvwrapper.sh
# /usr/bin/python

# Centos :
# /usr/bin/virtualenvwrapper.sh
# /usr/bin/python
# or for 2.7.13
# /opt/Python-2.7.13/bin/python2.7

echo "Python native"
/usr/bin/python --version

export VIRTUALENVWRAPPER_ENV_BIN_DIR=bin
export VIRTUALENVWRAPPER_HOOK_DIR=/var/lib/jenkins/.virtualenvs
export VIRTUALENVWRAPPER_LAZY_LOADED=1
export VIRTUALENVWRAPPER_PROJECT_FILENAME=.project
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
export VIRTUALENVWRAPPER_SCRIPT=/usr/share/virtualenvwrapper/virtualenvwrapper.sh
export VIRTUALENVWRAPPER_VIRTUALENV=virtualenv
export VIRTUALENVWRAPPER_VIRTUALENV_CLONE=virtualenv-clone
export VIRTUALENVWRAPPER_WORKON_CD=1

echo "=========================="
echo "Source"
echo "=========================="

. /usr/share/virtualenvwrapper/virtualenvwrapper.sh

echo "=========================="
echo "Init2"
echo "=========================="

PACKAGE_NAME=resolvusclient
PACKAGE_NAME_TEST=${PACKAGE_NAME}_test

echo "=========================="
echo "Clean last build job"
echo "=========================="

rm -fr /var/tmp/rpm-tmp.*
rm -fr /tmp/rpmvenv*

echo "=========================="
echo " Re-creating virtualenv '.env' for WORKSPACE=${WORKSPACE}"
echo "=========================="

ENV=.env

echo "Removing A"
rm -fr .env
echo "Removing B"
rmvirtualenv ${ENV}

echo "Virtualenv now"
# virtualenv ${ENV} -p /opt/Python-2.7.13/bin/python2.7
virtualenv ${ENV}

echo "Activate now"
source ${ENV}/bin/activate

echo "Python .env"
python --version
sleep 2

echo "=========================="
echo "Installing initial packages"
echo "=========================="

echo "Pip"
pip install pip --upgrade

echo "devpi-client"
pip install devpi-client --upgrade
if [ -n "$REPO_URL" ]; then
    echo "*** devpi toward REPO_URL=${REPO_URL}"
    devpi use --set-cfg ${REPO_URL}
fi

echo "setuptools"
pip install setuptools --upgrade

echo "TODO : Process debian pip"

echo "=========================="
echo "Installing requirements.txt, NOUSEWHEEL=${NOUSEWHEEL}"
echo "=========================="

pip install ${NOUSEWHEEL} -r requirements.txt

echo "=========================="
echo "Installing requirements_test.txt, NOUSEWHEEL=${NOUSEWHEEL}"
echo "=========================="

pip install ${NOUSEWHEEL} -r requirements_test.txt

echo "=========================="
echo "Processing versions"
echo "=========================="

sed  -i -e "/^p_version = / s/dev0/${BUILD_NUMBER}/" setup.py

sed -i "/BUILD_NUMBER/ s/BUILD_NUMBER/${BUILD_NUMBER}/"  debian/changelog

echo "=========================="
echo "Firing nosetests"
echo "=========================="

nosetests --where=${PACKAGE_NAME}_test -s --with-xunit --all-modules --traverse-namespace --with-xcoverage --cover-package=${PACKAGE_NAME} --cover-inclusive -A 'not prov'
echo toto
OUT=$?

echo "=========================="
echo "Got nosetests result, exitcode=${OUT}"
echo "=========================="

if [ ${OUT} -gt 0 ]; then
    echo "=========================="
    echo "ERROR, FAILED nosetests result, exit now [FATAL]"
    echo "=========================="
    exit ${OUT}
fi

echo "=========================="
echo "DEB BUILD CLEANUP"
echo "=========================="

echo "CLEANUP /var/lib/jenkins/workspace/"
rm -f /var/lib/jenkins/workspace/resolvusclient_*
rm -f /var/lib/jenkins/workspace/resolvusclient-*
rm -rf /var/lib/jenkins/workspace/resolvusclient@tmp

echo "CLEANUP : listing /var/lib/jenkins/workspace/"

ls -l /var/lib/jenkins/workspace/

echo "=========================="
echo "DEB BUILD EXPORT"
echo "=========================="

echo "EXPORT NOW (secret)"
export GPGKEY=0XTODO
export DEBEMAIL="llabatut@knock.center"
export DEBFULLNAME="Laurent Labatut"

echo "=========================="
echo "DEB BUILD GPG CHECK"
echo "=========================="

echo "CHECK : list-keys"
gpg --list-keys

echo "CHECK : list-secret-keys"
gpg --list-secret-keys

echo "CHECK : grip"
gpg --with-keygrip -k

echo "=========================="
echo "DEB BUILD GPG SIGN CHECK"
echo "=========================="

echo "CREATING FILE"
echo "toto" > ../toto.txt

echo "SIGNING FILE"
gpg --clear-sign ../toto.txt

echo "CAT ASC"
cat ../toto.txt.asc

echo "CLEANUP"
rm -f ../toto.txt
rm -f ../toto.txt.asc

echo "=========================="
echo "DEB BUILD INVOKE"
echo "=========================="

echo "REMOVE *.pyc"
find -name '*.pyc' -type f -delete

echo "BUILDING AMD64 DEB NOW (secret)"
dpkg-buildpackage --build=full --sign-key=B244D2C2D4535AE3AC44405894CD627B683855EB -rfakeroot

echo "=========================="
echo "DEB BUILD LIST"
echo "=========================="

echo "LISTING NOW"
ls -l /var/lib/jenkins/workspace/resolvusclient_*

echo "=========================="
echo "DEB UPLOAD GO"
echo "=========================="

echo "TODO TODO TODO"
echo "TODO TODO TODO"
echo "TODO TODO TODO"
echo "TODO TODO TODO"
echo "TODO TODO TODO"

echo "=========================="
echo "END OF SCRIPT"
echo "=========================="
exit 0