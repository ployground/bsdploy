# coding: utf-8
from bsdploy.bootstrap_utils import BootstrapUtils
from fabric.api import env, hide, run, settings
from ploy.common import yesno
from ploy.config import value_asbool

# a plain, default fabfile for jailhosts using mfsbsd


env.shell = '/bin/sh -c'


def bootstrap(**kwargs):
    """ bootstrap an instance booted into mfsbsd (http://mfsbsd.vx.sk)
    """
    env.shell = '/bin/sh -c'

    # default ssh settings for mfsbsd with possible overwrite by bootstrap-fingerprint
    fingerprint = env.instance.config.get(
        'bootstrap-fingerprint',
        '1f:cb:78:20:b8:97:dd:dc:3d:23:75:f0:bb:ad:84:03')
    env.instance.config['fingerprint'] = fingerprint
    env.instance.config['password-fallback'] = True
    env.instance.config['password'] = 'mfsroot'
    # allow overwrites from the commandline
    env.instance.config.update(kwargs)

    bu = BootstrapUtils()
    bu.generate_ssh_keys()
    bu.print_bootstrap_files()
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

    template_context = {}
    # first the config, so we don't get something essential overwritten
    template_context.update(env.instance.config)
    template_context.update(
        devices=bu.sysctl_devices,
        interfaces=bu.phys_interfaces,
        hostname=env.instance.id)

    rc_conf = bu.bootstrap_files['rc.conf'].read(template_context)
    if not rc_conf.endswith('\n'):
        print("\nERROR! Your rc.conf doesn't end in a newline:\n==========\n%s<<<<<<<<<<\n" % rc_conf)
        return
    rc_conf_lines = rc_conf.split('\n')

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

    yes = env.instance.config.get('bootstrap-yes', False)
    if not (yes or yesno("\nContinuing will destroy the existing data on the following devices:\n    %s\n\nContinue?" % ' '.join(bu.devices))):
        return

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
        zfsinstall=bu.zfsinstall,
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
    bu.create_bootstrap_directories()
    bu.upload_bootstrap_files(template_context)
    # we need to install python here, because there is no way to install it via
    # ansible playbooks
    bu.install_pkg('/mnt', chroot=True, packages=['python27'])
    # set autoboot delay
    autoboot_delay = env.instance.config.get('bootstrap-autoboot-delay', '-1')
    run('echo autoboot_delay=%s >> /mnt/boot/loader.conf' % autoboot_delay)
    bu.generate_remote_ssh_keys()
    # reboot
    if value_asbool(env.instance.config.get('bootstrap-reboot', 'true')):
        with settings(hide('warnings'), warn_only=True):
            run('reboot')


def fetch_assets(**kwargs):
    """ download bootstrap assets to control host.
    If present on the control host they will be uploaded to the target host during bootstrapping.
    """
    # allow overwrites from the commandline
    env.instance.config.update(kwargs)
    BootstrapUtils().fetch_assets()
