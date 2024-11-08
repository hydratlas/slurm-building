#!/usr/bin/env bash
set -eu
cd "$1"
apt-get update
mk-build-deps -i --tool 'apt-get -y' debian/control
debuild -b -uc -us
