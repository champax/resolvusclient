#!/usr/bin/env bash

# This can be fire manually, in /var/lib/jenkins/debug/resolvusclient for instance
# ie, where "resolvusclient" has been cloned
#
# Use :
# ./jenkins/_debug_manual.sh

# Set
JOB_NAME="resolvusclient"
BUILD_NUMBER="999"
JD="dummy"

# Export
export WORKSPACE="resolvusclient"
export NOUSEWHEEL=""
export REPO_URL=""

# Call
./jenkins/build_master.sh "${JOB_NAME}" "${BUILD_NUMBER}" "${JD}"