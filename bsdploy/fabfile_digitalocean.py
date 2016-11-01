# coding: utf-8
from bsdploy.bootstrap_utils import BootstrapUtils
from fabric.api import env, run, sudo
from time import sleep

# a plain, default fabfile for jailhosts on digital ocean


env.shell = '/bin/sh -c'


def bootstrap(**kwargs):
    """Digital Oceans FreeBSD droplets are pretty much already pre-bootstrapped,
    including having python2.7 and sudo etc. pre-installed.
    the only thing we need to change is to allow root to login (without a password)
    """
    original_host = env.host_string
    env.host_string = 'freebsd@%s' % env.instance.uid
    sudo("""sysrc pf_enable=YES""")
    sudo("""sysrc -f /boot/loader.conf pfload=YES""")
    sudo('kldload pf', warn_only=True)
    sudo('service pf start')
    sudo("""echo 'PermitRootLogin without-password' > /etc/ssh/sshd_config""")
    sudo("""service sshd fastreload""")
    # revert back to root
    env.host_string = original_host
    # give sshd a chance to restart
    sleep(2)

    # allow overwrites from the commandline
    env.instance.config.update(kwargs)

    bu = BootstrapUtils()
    bu.ssh_keys = None
    bu.upload_authorized_keys = False
