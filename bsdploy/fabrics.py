from __future__ import absolute_import, print_function
import os
import yaml
import sys
from bsdploy import bsdploy_path
from bsdploy.bootstrap_utils import BootstrapUtils
from fabric.api import env, put, run, settings, hide
from fabric.contrib.files import upload_template
from ploy.common import yesno
from ploy.config import value_asbool
from os.path import join, exists, abspath, dirname
from time import sleep
try:  # pragma: nocover
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: nocover
    from yaml import SafeLoader


def _fetch_packages(env, packagesite, packages):
    import tarfile
    try:
        import lzma
    except ImportError:
        print("ERROR: The lzma package couldn't be imported.")
        print("You most likely need to install pyliblzma in your virtualenv.")
        sys.exit(1)
    ploy_conf_path = join(env.instance.master.main_config.path)
    download_path = abspath(join(ploy_conf_path, '..', 'downloads'))
    packageinfo = {}
    print("Loading package information from '%s'." % packagesite)
    if SafeLoader.__name__ != 'CSafeLoader':
        print("WARNING: The C extensions for PyYAML aren't installed.")
        print("This can take quite a long while ...")
    else:
        print("This can take a while ...")
    for line in tarfile.TarFile(fileobj=lzma.LZMAFile(packagesite)).extractfile('packagesite.yaml'):
        info = yaml.load(line, Loader=SafeLoader)
        packageinfo[info['name']] = dict(
            path=info['path'],
            arch=info['arch'],
            deps=info.get('deps', {}).keys())
    deps = set(packages)
    seen = set()
    items = []
    while 1:
        try:
            dep = deps.pop()
        except KeyError:
            break
        if dep in seen:
            continue
        info = packageinfo[dep]
        deps.update(info['deps'])
        path = '%s/latest/%s' % (info['arch'], info['path'])
        items.append((
            join('packages', path),
            dict(
                url='http://pkg.freebsd.org/%s' % path,
                local=join(download_path, 'packages', path),
                remote=join('/mnt/var/cache/pkg/', info['path']))))
        seen.add(dep)
    return items


def fetch_assets(**kwargs):
    """ download bootstrap assets to control host.
    If present on the control host they will be uploaded to the target host during bootstrapping.
    """
    from fabric.api import env, local
    items = sorted(BootstrapUtils().bootstrap_files.items())
    packages = set(
        env.instance.master.instance.config.get('bootstrap-packages', '').split())
    packages.update(['python27'])
    for filename, asset in items:
        if 'url' in asset:
            if not exists(dirname(asset['local'])):
                os.makedirs(dirname(asset['local']))
            local('wget -c -O {local} {url} '.format(**asset))
        if filename == 'packagesite.txz':
            items.extend(_fetch_packages(env, asset['local'], packages))


def print_bootstrap_files(bootstrap_files):
    print("\nUsing these local files for bootstrapping:")
    for filename, info in sorted(bootstrap_files.items()):
        if 'remote' in info and exists(info['local']):
            if 'use_jinja' not in info:
                info['use_jinja'] = False
            print('{local} -(template:{use_jinja})-> {remote}'.format(**info))
    print("\nThe following files will be downloaded on the host during bootstrap:")
    for filename, info in sorted(bootstrap_files.items()):
        if 'remote' in info and 'url' in info and not exists(info['local']):
            print('{url} -> {remote}'.format(**info))
    print()


def bootstrap_mfsbsd(**kwargs):
    """ bootstrap an instance booted into mfsbsd (http://mfsbsd.vx.sk)
    """
    env.shell = '/bin/sh -c'

    bu = BootstrapUtils()

    print_bootstrap_files(bu.bootstrap_files)

    # default ssh settings for mfsbsd with possible overwrite by bootstrap-fingerprint
    fingerprint = env.instance.config.get(
        'bootstrap-fingerprint',
        '02:2e:b4:dd:c3:8a:b7:7b:ba:b2:4a:f0:ab:13:f4:2d')
    env.instance.config['fingerprint'] = fingerprint
    env.instance.config['password-fallback'] = True
    env.instance.config['password'] = 'mfsroot'
    # allow overwrites from the commandline
    env.instance.config.update(kwargs)

    # gather infos
    if not bu.bsd_url:
        print("Found no FreeBSD system to install, please specify bootstrap-bsd-url and make sure mfsbsd is running")
        return
    # get realmem here, because it may fail and we don't want that to happen
    # in the middle of the bootstrap
    realmem = bu.realmem
    print("\nFound the following disk devices on the system:\n    %s" % ' '.join(bu.sysctl_devices))
    if bu.first_interface:
        print("\nFound the following network interfaces, now is your chance to update your rc.conf accordingly!\n    %s" % ' '.join(bu.phys_interfaces))
    else:
        print("\nWARNING! Found no suitable network interface!")
    if not yesno("\nContinuing will destroy the existing data on the following devices:\n    %s\n\nContinue?" % ' '.join(bu.devices)):
        return

    template_context = {}
    # first the config, so we don't get something essential overwritten
    template_context.update(env.instance.config)
    template_context.update(
        devices=bu.sysctl_devices,
        interfaces=bu.phys_interfaces,
        hostname=env.instance.id)

    if bu.bootstrap_files['rc.conf'].get('use_jinja'):
        from jinja2 import Template
        template = Template(''.join(open(bu.bootstrap_files['rc.conf']['local']).readlines()))
        rc_conf_lines = template.render(**template_context).split('\n')
    else:
        rc_conf_lines = open(bu.bootstrap_files['rc.conf']['local'], 'r')

    for interface in [bu.first_interface, env.instance.config.get('ansible-dhcp_host_sshd_interface')]:
        if interface is None:
            continue
        ifconfig = 'ifconfig_%s' % interface
        for line in rc_conf_lines:
            if line.strip().startswith(ifconfig):
                break
        else:
            if not yesno("\nDidn't find an '%s' setting in rc.conf. You sure that you want to continue?" % ifconfig):
                return
    zfsinstall = env.instance.config.get('bootstrap-zfsinstall')
    if zfsinstall:
        put(abspath(join(env.instance.master.main_config.path, zfsinstall)), '/root/bin/myzfsinstall', mode=0755)
        zfsinstall = 'myzfsinstall'
    else:
        zfsinstall = 'zfsinstall'
    # install FreeBSD in ZFS root
    devices_args = ' '.join('-d %s' % x for x in bu.devices)
    system_pool_name = env.instance.config.get('bootstrap-system-pool-name', 'system')
    data_pool_name = env.instance.config.get('bootstrap-data-pool-name', 'tank')
    swap_arg = ''
    swap_size = env.instance.config.get('bootstrap-swap-size', '%iM' % (realmem * 2))
    if swap_size:
        swap_arg = '-s %s' % swap_size
    system_pool_arg = ''
    system_pool_size = env.instance.config.get('bootstrap-system-pool-size', '20G')
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
        bsd_url=bu.bsd_url,
        swap_arg=swap_arg,
        system_pool_arg=system_pool_arg))
    # create partitions for data pool, but only if the system pool doesn't use
    # the whole disk anyway
    if system_pool_arg:
        for device in bu.devices:
            run('gpart add -t freebsd-zfs -l {data_pool_name}_{device} {device}'.format(
                data_pool_name=data_pool_name,
                device=device))
    # mount devfs inside the new system
    if 'devfs on /rw/dev' not in bu.mounts:
        run('mount -t devfs devfs /mnt/dev')
    # setup bare essentials
    run('cp /etc/resolv.conf /mnt/etc/resolv.conf')
    for filename, info in sorted(bu.bootstrap_files.items()):
        if 'directory' not in info:
            continue
        cmd = 'mkdir -p "%s"' % info['directory']
        if 'directory_mode' in info:
            cmd = '%s && chmod %s "%s"' % (cmd, info['directory_mode'], info['directory'])
        run(cmd, shell=False)

    # upload bootstrap files
    for filename, info in sorted(bu.bootstrap_files.values()):
        if 'remote' in info and exists(info['local']):
            if info.get('use_jinja'):
                template_dir, template_name = os.path.split(info['local'])
                upload_template(
                    template_name,
                    info['remote'],
                    context=template_context,
                    use_jinja=True,
                    template_dir=template_dir,
                    mode=info.get('mode'))
            else:
                put(info['local'], info['remote'], mode=info.get('mode'))

    # install pkg, the tarball is also used for the ezjail flavour in bootstrap_ezjail
    if not exists(bu.bootstrap_files['pkg.txz']['local']):
        run('fetch -o {remote} {url}'.format(**bu.bootstrap_files['pkg.txz']))
    run('chmod 0600 {remote}'.format(**bu.bootstrap_files['pkg.txz']))
    run("tar -x -C /mnt --chroot --exclude '+*' -f {remote}".format(**bu.bootstrap_files['pkg.txz']))
    # run pkg2ng for which the shared library path needs to be updated
    run('chroot /mnt /etc/rc.d/ldconfig start')
    run('chroot /mnt pkg2ng')
    # we need to install python here, because there is no way to install it via
    # ansible playbooks
    run('chroot /mnt pkg install python27')
    # set autoboot delay
    autoboot_delay = env.instance.config.get('bootstrap-autoboot-delay', '-1')
    run('echo autoboot_delay=%s >> /mnt/boot/loader.conf' % autoboot_delay)
    # ssh host keys
    for ssh_key, ssh_keygen_args in sorted(bu.ssh_keys):
        if ssh_key not in bu.bootstrap_files:
            run("ssh-keygen %s -f /mnt/etc/ssh/%s -N ''" % (ssh_keygen_args, ssh_key))
    fingerprint = run("ssh-keygen -lf /mnt/etc/ssh/ssh_host_rsa_key")
    # reboot
    if value_asbool(env.instance.config.get('bootstrap-reboot', 'true')):
        with settings(hide('warnings'), warn_only=True):
            run('reboot')
    print("The SSH fingerprint of the newly bootstrapped server is:")
    print(fingerprint)


def bootstrap_daemonology(**kwargs):
    """ Bootstrap an EC2 instance that has been booted into an AMI from http://www.daemonology.net/freebsd-on-ec2/
    """
    # the user for the image is `ec2-user`, there is no sudo, but we can su to root w/o password
    original_host = env.host_string
    env.host_string = 'ec2-user@%s' % env.instance.uid
    put('etc/authorized_keys', '/tmp/authorized_keys')
    put(os.path.join(bsdploy_path, 'enable_root_login_on_daemonology.sh'), '/tmp/', mode='0775')
    run("""su root -c '/tmp/enable_root_login_on_daemonology.sh'""")
    # revert back to root
    env.host_string = original_host
    # give sshd a chance to restart
    sleep(2)
    run('rm /tmp/enable_root_login_on_daemonology.sh')

    bu = BootstrapUtils()
    bu.ssh_keys = None
    bu.upload_authorized_keys = False
    bu.bootstrap_files_yaml = 'daemonology-files.yml'

    print_bootstrap_files(bu.bootstrap_files)

    # allow overwrites from the commandline
    env.instance.config.update(kwargs)

    for filename, info in sorted(bu.bootstrap_files.items()):
        if 'directory' not in info:
            continue
        cmd = 'mkdir -p "%s"' % info['directory']
        if 'directory_mode' in info:
            cmd = '%s && chmod %s "%s"' % (cmd, info['directory_mode'], info['directory'])
        run(cmd, shell=False)

    # upload bootstrap files
    for filename, info in sorted(bu.bootstrap_files.items()):
        if 'remote' in info and exists(info['local']):
            put(info['local'], info['remote'], mode=info.get('mode'))

    # install pkg, the tarball is also used for the ezjail flavour in bootstrap_ezjail
    if not exists(bu.bootstrap_files['pkg.txz']['local']):
        run('fetch -o {remote} {url}'.format(**bu.bootstrap_files['pkg.txz']))
    run('chmod 0600 {remote}'.format(**bu.bootstrap_files['pkg.txz']))
    run("tar -x -C / --exclude '+*' -f {remote}".format(**bu.bootstrap_files['pkg.txz']))
    # run pkg2ng for which the shared library path needs to be updated
    run('/etc/rc.d/ldconfig start')
    run('pkg2ng')
    # we need to install python here, because there is no way to install it via
    # ansible playbooks
    run('pkg install python27')
