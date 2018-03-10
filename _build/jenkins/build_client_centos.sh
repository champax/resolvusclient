#!/bin/bash -e

echo "=========================="
echo "build_client_centos.sh called"
echo "=========================="

echo "=========================="
echo "Init"
echo "=========================="

# Debian :
# /usr/local/bin/virtualenvwrapper.sh
# /usr/local/bin/python

# Centos :
# /usr/bin/virtualenvwrapper.sh
# /usr/bin/python
# or for 2.7.13
# /opt/Python-2.7.13/bin/python2.7

echo "Python native"
python --version

echo "Python opt"
/opt/Python-2.7.13/bin/python2.7 --version



export VIRTUALENVWRAPPER_ENV_BIN_DIR=bin
export VIRTUALENVWRAPPER_HOOK_DIR=/var/lib/jenkins/.virtualenvs
export VIRTUALENVWRAPPER_LAZY_LOADED=1
export VIRTUALENVWRAPPER_PROJECT_FILENAME=.project
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
export VIRTUALENVWRAPPER_SCRIPT=/usr/bin/virtualenvwrapper.sh
export VIRTUALENVWRAPPER_VIRTUALENV=virtualenv
export VIRTUALENVWRAPPER_VIRTUALENV_CLONE=virtualenv-clone
export VIRTUALENVWRAPPER_WORKON_CD=1

echo "=========================="
echo "Source"
echo "=========================="


. /usr/bin/virtualenvwrapper.sh

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
virtualenv ${ENV} -p /opt/Python-2.7.13/bin/python2.7

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

echo "rpmvenv"
pip install rpmvenv --upgrade

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
sed -i "/BUILD_NUMBER/ s/BUILD_NUMBER/${BUILD_NUMBER}/"  redhat/config_rpm.json

echo "=========================="
echo "Firing nosetests"
echo "=========================="

nosetests --where=${PACKAGE_NAME}_test -s --with-xunit --all-modules --traverse-namespace --with-xcoverage --cover-package=${PACKAGE_NAME} --cover-inclusive -A 'not prov'
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
echo "Pushing additionnal python stuff (/opt/Python-2.7.13/lib/python2.7 => additional_lib => /opt/resolvusclient/lib/python2.7/"
echo "=========================="

rm -rf ./additional_lib
mkdir -p ./additional_lib
cp -r /opt/Python-2.7.13/lib/python2.7/* ./additional_lib

echo "=========================="
echo "Packaging rpm"
echo "=========================="

echo "Deleting existing rpm"
rm -f ./*.rpm

echo "Firing rpmvenv now"
# rpmvenv --verbose  redhat/config_rpm.json  --source .
rpmvenv redhat/config_rpm.json  --source .

echo "=========================="
echo "RPM LOCAL FILE"
echo "=========================="

pwd

ls -l ./resolvusclient-*.rpm

echo "=========================="
echo "Debug section"
echo "=========================="

echo "Resetting rpmvenv target dir=/tmp/rpm_resolvusclient"
rm -rf /tmp/rpm_resolvusclient
mkdir /tmp/rpm_resolvusclient


cp ./resolvusclient-*.rpm /tmp/rpm_resolvusclient/
cd /tmp/rpm_resolvusclient/

# echo "Extracting for check"
# rpm2cpio ./resolvusclient-*.rpm | cpio -idmv

# echo "Listing rpm file"
# rpm -qlp ./resolvusclient-*.rpm

echo "Dependencies below"
yum deplist ./resolvusclient-*.rpm

cd -

echo "=========================="
echo "Pushing RPM"
echo "=========================="

echo "SCP : Skipped"
# TODO : Push RPM toward RPM internal repo
# scp vulgo*.rpm TODOSERVER:/var/lib/rpm_repos_beta/centos/7/os/x86_64/
# ssh TODOSERVER createrepo --update /var/lib/rpm_repos_beta/centos/7/os/x86_64/

echo "Pushing to /var/lib/jenkins/resolvus_rpm_store/"
mkdir -p /var/lib/jenkins/resolvus_rpm_store
cp ./resolvusclient-*.rpm /var/lib/jenkins/resolvus_rpm_store/

echo "Listing /var/lib/jenkins/resolvus_rpm_store/"
ls -ltr /var/lib/jenkins/resolvus_rpm_store/

echo "=========================="
echo "OVER"
echo "=========================="