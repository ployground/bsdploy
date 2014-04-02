from __future__ import absolute_import, print_function
import sys
from mr.awsome.common import yesno
from os.path import join, expanduser, exists, abspath
from . import ploy_path


def get_bootstrap_files(env, ssh_keys=None):
    """ we need some files to bootstrap the FreeBSD installation.
    Some...
        - need to be provided by the user (i.e. authorized_keys)
        - others have some (sensible) defaults (i.e. rc.conf)
        - some can be downloaded via URL (i.e.) http://pkg.freebsd.org/freebsd:9:x86:64/latest/Latest/pkg.txz

    For those which can be downloaded we check the downloads directory. if the file exists there
    (and if the checksum matches TODO!) we will upload it to the host. If not, we will fetch the file
    from the given URL from the host.

    For files that cannot be downloaded (authorized_keys, rc.conf etc.) we allow the user to provide their
    own version in a ``bootstrap-files`` folder. The location of this folder can either be explicitly provided
    via the ``bootstrap-files`` key in the host definition of the config file or it defaults to ``deployment/bootstrap-files``.

    If the file is not found there, we revert to the default
    files that are part of bsdploy. If the file cannot be found there either we either error out or for authorized_keys
    we look in ``~/.ssh/identity.pub``.
    """

    ploy_conf_path = join(env.server.master.main_config.path)
    default_template_path = join(ploy_path, 'bootstrap-files')
    host_defined_path = env.server.master.instance.config.get('bootstrap-files')
    if host_defined_path is None:
        custom_template_path = abspath(join(ploy_conf_path, '..', 'deployment', 'bootstrap-files'))
    else:
        custom_template_path = abspath(join(ploy_conf_path, host_defined_path))
    download_path = abspath(join(ploy_conf_path, '..', 'downloads'))
    bootstrap_files = {
        'authorized_keys': {
            'remote': '/mnt/root/.ssh/authorized_keys',
            'expected_path': ploy_conf_path,
            'fallback': expanduser('~/.ssh/identity.pub')},
        'rc.conf': {
            'remote': '/mnt/etc/rc.conf'},
        'make.conf': {
            'remote': '/mnt/etc/make.conf'},
        'pkg.conf': {
            'remote': '/mnt/usr/local/etc/pkg.conf'},
        'FreeBSD.conf': {
            'remote': '/mnt/usr/local/etc/pkg/repos/FreeBSD.conf'},
        'sshd_config': {
            'remote': '/mnt/etc/ssh/sshd_config'},
        'pkg.txz': {
            'url': 'http://pkg.freebsd.org/freebsd:9:x86:64/latest/Latest/pkg.txz',
            'remote': '/mnt/var/cache/pkg/All/pkg.txz'},
        'mfsbsd-se-9.2-RELEASE-amd64.iso': {
            'url': 'http://mfsbsd.vx.sk/files/iso/9/amd64/mfsbsd-se-9.2-RELEASE-amd64.iso',
            'md5': '660d2b65e55a982c071891b7996fe684'},
    }

    for filename, info in bootstrap_files.items():
        if 'expected_path' in info:
            expected_path = info['expected_path']
        elif 'url' in info:
            expected_path = download_path
        else:
            expected_path = custom_template_path

        local_path = join(expected_path, filename)

        if not exists(local_path) and 'fallback' in info:
            print("The '%s' file is missing." % local_path)
            local_path = info['fallback']
            if not yesno("Should we generate it using the key in '%s'?" % local_path):
                sys.exit(1)

        if not exists(local_path) and 'url' not in info:
            local_path = join(default_template_path, filename)

        if not exists(local_path) and 'url' not in info:
            print('Cannot find %s' % local_path)
            sys.exit(1)

        bootstrap_files[filename]['local'] = local_path

    if ssh_keys is not None:
        for ssh_key_name, ssh_key_options in list(ssh_keys):
            ssh_key = join(custom_template_path, ssh_key_name)
            if exists(ssh_key):
                pub_key_name = '%s.pub' % ssh_key_name
                pub_key = '%s.pub' % ssh_key
                if not exists(pub_key):
                    print("Public key '%s' for '%s' missing." % (pub_key, ssh_key))
                    sys.exit(1)
                bootstrap_files[ssh_key_name] = dict(local=ssh_key, remote='/mnt/etc/ssh/%s' % ssh_key_name, mode=0600)
                bootstrap_files[pub_key_name] = dict(local=pub_key, remote='/mnt/etc/ssh/%s' % pub_key_name, mode=0644)
    return bootstrap_files


def fetch_assets(**kwargs):
    from fabric.api import env, local
    bootstrap_files = get_bootstrap_files(env)
    for filename, asset in bootstrap_files.items():
        if 'url' in asset:
            local('wget -c -O {local} {url} '.format(**asset))


def bootstrap(**kwargs):
    from fabric.api import env, put, run, settings, hide
    from mr.awsome.config import value_asbool
    import math
    env.shell = '/bin/sh -c'

    ssh_keys = set([
        ('ssh_host_key', '-t rsa1 -b 1024'),
        ('ssh_host_rsa_key', '-t rsa'),
        ('ssh_host_dsa_key', '-t dsa'),
        ('ssh_host_ecdsa_key', '-t ecdsa')])

    bootstrap_files = get_bootstrap_files(env, ssh_keys=ssh_keys)

    print("Using these local files for bootstrapping:")
    for info in bootstrap_files.values():
        if 'remote' in info:
            print('{local} -> {remote}'.format(**info))
    # default ssh settings for mfsbsd with possible overwrite by bootstrap-fingerprint
    fingerprint = env.server.config.get(
        'bootstrap-fingerprint',
        '02:2e:b4:dd:c3:8a:b7:7b:ba:b2:4a:f0:ab:13:f4:2d')
    env.server.config['fingerprint'] = fingerprint
    env.server.config['password-fallback'] = True
    env.server.config['password'] = 'mfsroot'
    # allow overwrites from the commandline
    env.server.config.update(kwargs)
    # gather infos
    with settings(hide('output')):
        mounts = run('mount')
        sysctl_devices = run('sysctl -n kern.disks').strip().split()
        realmem = run('sysctl -n hw.realmem').strip()
        realmem = float(realmem) / 1024 / 1024
        realmem = 2 ** int(math.ceil(math.log(realmem, 2)))
        interfaces = run('ifconfig -l').strip()
    cd_device = env.server.config.get('bootstrap-cd-device', 'cd0')
    if '/dev/{dev} on /rw/cdrom'.format(dev=cd_device) not in mounts:
        run('test -e /dev/{dev} && mount_cd9660 /dev/{dev} /cdrom || true'.format(dev=cd_device))
    usb_device = env.server.config.get('bootstrap-usb-device', 'da0a')
    if '/dev/{dev} on /rw/media'.format(dev=usb_device) not in mounts:
        run('test -e /dev/{dev} && mount -o ro /dev/{dev} /media || true'.format(dev=usb_device))
    bsd_url = env.server.config.get('bootstrap-bsd-url')
    if not bsd_url:
        with settings(hide('output', 'warnings'), warn_only=True):
            result = run("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \;")
            if result.return_code == 0:
                bsd_url = result.strip()
    if not bsd_url:
        print("Found no FreeBSD system to install, please specify bootstrap-bsd-url and make sure mfsbsd is running")
        return
    install_devices = [cd_device, usb_device]
    devices = set(sysctl_devices)
    for sysctl_device in sysctl_devices:
        for install_device in install_devices:
            if install_device.startswith(sysctl_device):
                devices.remove(sysctl_device)
    devices = env.server.config.get('bootstrap-system-devices', ' '.join(devices)).split()
    print("\nFound the following disk devices on the system:\n    %s" % ' '.join(sysctl_devices))
    real_interfaces = [x for x in interfaces.split() if not x.startswith('lo')]
    if len(real_interfaces):
        print("\nFound the following network interfaces, now is your chance to update your rc.conf accordingly!\n    %s" % ' '.join(real_interfaces))
        first_interface = real_interfaces[0]
    else:
        print("\nWARNING! Found no suitable network interface!")
        first_interface = None
    if not yesno("\nContinuing will destroy the existing data on the following devices:\n    %s\n\nContinue?" % ' '.join(devices)):
        return
    if first_interface is not None:
        ifconfig = 'ifconfig_%s' % first_interface
        for line in open(bootstrap_files['rc.conf']['local']):
            if line.strip().startswith(ifconfig):
                break
        else:
            if not yesno("\nDidn't find an '%s' setting in rc.conf. You sure that you want to continue?" % ifconfig):
                return
    zfsinstall = env.server.config.get('bootstrap-zfsinstall')
    if zfsinstall:
        put(abspath(join(env.server.master.main_config.path, zfsinstall)), '/root/bin/myzfsinstall', mode=0755)
        zfsinstall = 'myzfsinstall'
    else:
        zfsinstall = 'zfsinstall'
    # install FreeBSD in ZFS root
    devices_args = ' '.join('-d %s' % x for x in devices)
    system_pool_name = env.server.config.get('bootstrap-system-pool-name', 'system')
    data_pool_name = env.server.config.get('bootstrap-data-pool-name', 'tank')
    swap_arg = ''
    swap_size = env.server.config.get('bootstrap-swap-size', '%iM' % (realmem * 2))
    if swap_size:
        swap_arg = '-s %s' % swap_size
    system_pool_arg = ''
    system_pool_size = env.server.config.get('bootstrap-system-pool-size', '20G')
    if system_pool_size:
        system_pool_arg = '-z %s' % system_pool_size
    run('destroygeom {devices_args} -p {system_pool_name} -p {data_pool_name}'.format(
        devices_args=devices_args,
        system_pool_name=system_pool_name,
        data_pool_name=data_pool_name))
    run('{zfsinstall} {devices_args} -p {system_pool_name} -V 28 -u {bsd_url} {swap_arg} {system_pool_arg}'.format(
        zfsinstall=zfsinstall,
        devices_args=devices_args,
        system_pool_name=system_pool_name,
        bsd_url=bsd_url,
        swap_arg=swap_arg,
        system_pool_arg=system_pool_arg))
    # create partitions for data pool, but only if the system pool doesn't use
    # the whole disk anyway
    if system_pool_arg:
        for device in devices:
            run('gpart add -t freebsd-zfs -l {data_pool_name}_{device} {device}'.format(
                data_pool_name=data_pool_name,
                device=device))
    # mount devfs inside the new system
    if 'devfs on /rw/dev' not in mounts:
        run('mount -t devfs devfs /mnt/dev')
    # setup bare essentials
    run('mkdir -p /mnt/root/.ssh && chmod 0600 /mnt/root/.ssh')
    run('cp /etc/resolv.conf /mnt/etc/resolv.conf')
    run('mkdir -p /mnt/usr/local/etc/pkg/repos')
    run('mkdir -p /mnt/var/cache/pkg/All')

    # upload bootstrap files
    for info in bootstrap_files.values():
        if 'remote' in info and exists(info['local']):
            put(info['local'], info['remote'], mode=info.get('mode'))

    # install pkg, the tarball is also used for the ezjail flavour in bootstrap_ezjail
    if not exists(bootstrap_files['pkg.txz']['local']):
        run('fetch -o {remote} {url}'.format(**bootstrap_files['pkg.txz']))
    run('chmod 0600 {remote}'.format(**bootstrap_files['pkg.txz']))
    run("tar -x -C /mnt --chroot --exclude '+*' -f {remote}".format(**bootstrap_files['pkg.txz']))
    # run pkg2ng for which the shared library path needs to be updated
    run('chroot /mnt /etc/rc.d/ldconfig start')
    run('chroot /mnt pkg2ng')
    # we need to install python here, because there is no way to install it via
    # ansible playbooks
    run('chroot /mnt pkg install python27')
    # set autoboot delay
    autoboot_delay = env.server.config.get('bootstrap-autoboot-delay', '-1')
    run('echo autoboot_delay=%s >> /mnt/boot/loader.conf' % autoboot_delay)
    # ssh host keys
    for ssh_key, ssh_keygen_args in ssh_keys:
        if ssh_key not in bootstrap_files:
            run("ssh-keygen %s -f /mnt/etc/ssh/%s -N ''" % (ssh_keygen_args, ssh_key))
    fingerprint = run("ssh-keygen -lf /mnt/etc/ssh/ssh_host_rsa_key")
    # reboot
    if value_asbool(env.server.config.get('bootstrap-reboot', 'true')):
        with settings(hide('warnings'), warn_only=True):
            run('reboot')
    print("The SSH fingerprint of the newly bootstrapped server is:")
    print(fingerprint)
