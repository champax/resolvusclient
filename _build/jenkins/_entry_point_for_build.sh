#!/bin/bash

# This must be set in Jenkins => Build, Execute shell

# Export
export JOB_NAME=${JOB_NAME}
export BUILD_NUMBER=${BUILD_NUMBER}
export JD=${JD}

# Debug
echo "JOB_NAME=${JOB_NAME}"
echo "BUILD_NUMBER=${BUILD_NUMBER}"
echo "JD=${JD}"

# Fire
jenkins/build_master.sh "${JOB_NAME}"  "${BUILD_NUMBER}" "${JD}"