#!/bin/sh
exec 1>/var/log/startup.log 2>&1
chmod 0600 /var/log/startup.log
set -e
set -x
pkg update
pkg upgrade
pkg install python2
