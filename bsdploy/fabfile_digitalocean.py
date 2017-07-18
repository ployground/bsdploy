# coding: utf-8
from bsdploy.bootstrap_utils import BootstrapUtils
from fabric.api import env, sudo, run, put, task
from os import path
from time import sleep

# a plain, default fabfile for jailhosts on digital ocean


env.shell = '/bin/sh -c'


@task
def bootstrap(**kwargs):
    """Digital Oceans FreeBSD droplets are pretty much already pre-bootstrapped,
    including having python2.7 and sudo etc. pre-installed.
    the only thing we need to change is to allow root to login (without a password)
    enable pf and ensure it is running
    """

    bu = BootstrapUtils()
    # (temporarily) set the user to `freebsd`
    original_host = env.host_string
    env.host_string = 'freebsd@%s' % env.instance.uid
    # copy DO bsdclout-init results:
    if bu.os_release.startswith('10'):
        sudo("""cat /etc/rc.digitalocean.d/droplet.conf > /etc/rc.conf""")
    sudo("""sysrc zfs_enable=YES""")
    sudo("""sysrc sshd_enable=YES""")
    # enable and start pf
    sudo("""sysrc pf_enable=YES""")
    sudo("""sysrc -f /boot/loader.conf pfload=YES""")
    sudo('kldload pf', warn_only=True)
    sudo('''echo 'pass in all' > /etc/pf.conf''')
    sudo('''echo 'pass out all' >> /etc/pf.conf''')
    sudo('''chmod 644 /etc/pf.conf''')
    sudo('service pf start')
    # overwrite sshd_config, because the DO version only contains defaults
    # and a line explicitly forbidding root to log in
    sudo("""echo 'PermitRootLogin without-password' > /etc/ssh/sshd_config""")
    # additionally, make sure the root user is unlocked!
    sudo('pw unlock root')
    # overwrite the authorized keys for root, because DO creates its entries to explicitly
    # disallow root login
    bootstrap_files = env.instance.config.get('bootstrap-files', 'bootstrap-files')
    put(path.abspath(path.join(env['config_base'], bootstrap_files, 'authorized_keys')), '/tmp/authorized_keys', use_sudo=True)
    sudo('''mv /tmp/authorized_keys /root/.ssh/''')
    sudo('''chown root:wheel /root/.ssh/authorized_keys''')

    sudo("""service sshd fastreload""")
    # revert back to root
    env.host_string = original_host
    # give sshd a chance to restart
    sleep(2)
    # clean up DO cloudinit leftovers
    run("rm -f /etc/rc.d/digitalocean")
    run("rm -rf /etc/rc.digitalocean.d")
    run("rm -rf /usr/local/bsd-cloudinit/")
    run("pkg remove -y avahi-autoipd || true")

    # allow overwrites from the commandline
    env.instance.config.update(kwargs)

    bu.ssh_keys = None
    bu.upload_authorized_keys = False
