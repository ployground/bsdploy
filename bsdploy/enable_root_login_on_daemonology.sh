#!/bin/sh
mkdir /root/.ssh
chmod 700 /root/.ssh
chmod 600 /tmp/authorized_keys
mv /tmp/authorized_keys /root/.ssh/
chown root /root/.ssh/authorized_keys
echo "PermitRootLogin without-password" >> /etc/ssh/sshd_config
/etc/rc.d/sshd fastreload