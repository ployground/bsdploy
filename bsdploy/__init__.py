from glob import glob
from os import path
import argparse
import logging
import sys


log = logging.getLogger("bsdploy")


# register our own library and roles paths into ansible
bsdploy_path = path.abspath(path.dirname(__file__))

ansible_paths = dict(
    roles=[path.join(bsdploy_path, 'roles')],
    library=[path.join(bsdploy_path, 'library')])

virtualbox_instance_defaults = {
    'vm-ostype': 'FreeBSD_64',
    'vm-memory': '2048',
    'vm-accelerate3d': 'off',
    'vm-acpi': 'on',
    'vm-rtcuseutc': 'on',
    'vm-boot1': 'disk',
    'vm-boot2': 'dvd',
    'vm-nic1': 'hostonly',
    'vm-hostonlyadapter1': 'vboxnet0',
}

virtualbox_hostonlyif_defaults = {
    'ip': '192.168.56.1',
}

virtualbox_dhcpserver_defaults = {
    'ip': '192.168.56.2',
    'netmask': '255.255.255.0',
    'lowerip': '192.168.56.100',
    'upperip': '192.168.56.254',
}

virtualbox_bootdisk_defaults = {
    'size': '102400',
}


ez_instance_defaults = {
    'ansible_python_interpreter': '/usr/local/bin/python2.7',
    'fabric-shell': '/bin/sh -c',
}


class PloyBootstrapCmd(object):
    def __init__(self, ctrl):
        self.ctrl = ctrl

    def __call__(self, argv, help):
        """Bootstrap a jailhost that's been booted into MFSBsd."""
        parser = argparse.ArgumentParser(
            prog="%s bootstrap" % self.ctrl.progname,
            description=help)
        masters = dict((master.id, master) for master in self.ctrl.get_masters('ezjail_admin'))
        parser.add_argument(
            "master",
            nargs='?' if len(masters) == 1 else 1,
            metavar="master",
            help="Name of the jailhost from the config.",
            choices=masters,
            default=masters.keys()[0] if len(masters) == 1 else None)
        parser.add_argument(
            "-y", "--yes", action="store_true",
            help="Answer yes to all questions.")
        parser.add_argument(
            "-p", "--http-proxy",
            help="Use http proxy for bootstrapping and pkg installation")
        args = parser.parse_args(argv)
        master = args.master if len(masters) == 1 else args.master[0]
        instance = self.ctrl.instances[master]
        instance.hooks.before_bsdploy_bootstrap(instance)
        bootstrap_args = {'bootstrap-yes': args.yes}
        if args.http_proxy:
            bootstrap_args['http_proxy'] = args.http_proxy
        instance.do('bootstrap', **bootstrap_args)
        instance.hooks.after_bsdploy_bootstrap(instance)


def get_bootstrap_path(instance):
    host_defined_path = instance.config.get('bootstrap-files')
    ploy_conf_path = instance.master.main_config.path
    if host_defined_path is None:
        bootstrap_path = path.join(ploy_conf_path, '..', 'bootstrap-files')
    else:
        bootstrap_path = path.join(ploy_conf_path, host_defined_path)
    return bootstrap_path


def get_ssh_key_paths(instance):
    bootstrap_path = get_bootstrap_path(instance)
    key_paths = []
    for ssh_key in glob(path.join(bootstrap_path, 'ssh_host*_key.pub')):
        ssh_key = path.abspath(ssh_key)
        key_paths.append(ssh_key)
    return key_paths


def augment_instance(instance):
    from ploy_ansible import get_ansible_version, get_playbooks_directory
    from ploy_ansible import has_playbook
    from ploy.config import ConfigSection

    if get_ansible_version() < (1, 5):
        log.error("You have an Ansible version below 1.5.0, which isn't supported anymore.")
        sys.exit(1)

    main_config = instance.master.main_config

    # provide virtualbox specific convenience defaults:
    if instance.master.sectiongroupname == ('vb-instance'):

        # default values for virtualbox instance
        for key, value in virtualbox_instance_defaults.items():
            instance.config.setdefault(key, value)

        # default hostonly interface
        hostonlyif = main_config.setdefault('vb-hostonlyif', ConfigSection())
        vboxnet0 = hostonlyif.setdefault('vboxnet0', ConfigSection())
        for key, value in virtualbox_hostonlyif_defaults.items():
            vboxnet0.setdefault(key, value)

        # default dhcp server
        dhcpserver = main_config.setdefault('vb-dhcpserver', ConfigSection())
        vboxnet0 = dhcpserver.setdefault('vboxnet0', ConfigSection())
        for key, value in virtualbox_dhcpserver_defaults.items():
            vboxnet0.setdefault(key, value)

        # default virtual disk
        if 'vb-disk:defaultdisk' in instance.config.get('storage', {}):
            disks = main_config.setdefault('vb-disk', ConfigSection())
            defaultdisk = disks.setdefault('defaultdisk', ConfigSection())
            for key, value in virtualbox_bootdisk_defaults.items():
                defaultdisk.setdefault(key, value)

    if not instance.master.sectiongroupname.startswith('ez-'):
        return

    for key, value in ez_instance_defaults.items():
        instance.config.setdefault(key, value)

    if 'fabfile' not in instance.config:
        playbooks_directory = get_playbooks_directory(main_config)
        fabfile = path.join(playbooks_directory, instance.uid, 'fabfile.py')
        if path.exists(fabfile):
            instance.config['fabfile'] = fabfile

    if instance.master.instance is instance:
        # for hosts
        if 'fabfile' not in instance.config:
            bootstrap_type = instance.config.get('bootstrap', 'mfsbsd')
            fabfile = path.join(bsdploy_path, 'fabfile_%s.py' % bootstrap_type)
            instance.config['fabfile'] = fabfile
        if not path.exists(instance.config['fabfile']):
            log.error("The fabfile '%s' for instance '%s' doesn't exist." % (
                instance.config['fabfile'], instance.uid))
            sys.exit(1)
        if not has_playbook(instance):
            instance.config['roles'] = 'jails_host'
        if 'ssh-host-keys' not in instance.config:
            key_paths = get_ssh_key_paths(instance)
            instance.config['ssh-host-keys'] = "\n".join(key_paths)
    else:
        # for jails
        instance.config.setdefault('startup_script', path.join(
            bsdploy_path, 'startup-ansible-jail.sh'))
        instance.config.setdefault('flavour', 'bsdploy_base')


def get_commands(ctrl):
    return [('bootstrap', PloyBootstrapCmd(ctrl))]


plugin = dict(
    augment_instance=augment_instance,
    get_commands=get_commands)
