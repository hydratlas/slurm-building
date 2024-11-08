#!/usr/bin/env bash
set -eu
apt-get update
mk-build-deps -i --tool 'apt-get -y' debian/control
debuild -b -uc -us
