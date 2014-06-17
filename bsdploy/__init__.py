import argparse
from pkg_resources import get_distribution
from mr.awsome import aws, aws_ssh
from os import path


# register our own library and roles paths into ansible
ploy_path = path.abspath(path.join(path.dirname(__file__), '../'))

ansible_paths = dict(
    roles=[path.join(ploy_path, 'roles')],
    library=[path.join(ploy_path, 'library')]
)


class PloyBootstrapCmd(object):

    def __init__(self, aws):
        self.aws = aws

    def __call__(self, argv, help):
        """Bootstrap a jailhost that's been booted into MFSBsd."""
        parser = argparse.ArgumentParser(
            prog="ploy bootstrap",
            description=help)
        masters = dict((master.id, master) for master in self.aws.get_masters('ezjail_admin'))
        parser.add_argument(
            "master",
            nargs='?' if len(masters) == 1 else 1,
            metavar="master",
            help="Name of the jailhost from the config.",
            choices=masters,
            default=masters.keys()[0] if len(masters) == 1 else None)
        args = parser.parse_args(argv)
        master = args.master if len(masters) == 1 else args.master[0]
        instance = self.aws.instances[master]
        instance.hooks.before_bsdploy_bootstrap(instance)
        instance.do('bootstrap')
        instance.hooks.after_bsdploy_bootstrap(instance)


def augment_instance(instance):
    from mr.awsome_ansible import has_playbook
    if not instance.master.sectiongroupname.startswith('ez-'):
        return
    if 'ansible_python_interpreter' not in instance.config:
        instance.config['ansible_python_interpreter'] = '/usr/local/bin/python2.7'
    if instance.master.instance is instance:
        # for hosts
        if 'fabfile' not in instance.config:
            bootstrap_type = instance.config.get('bootstrap', 'mfsbsd')
            fabfile = path.join(
                path.abspath(path.dirname(__file__)),
                'fabfile_%s.py' % bootstrap_type)
            instance.config['fabfile'] = fabfile
        if not has_playbook(instance):
            instance.config['roles'] = 'dhcp_host jails_host'
    else:
        # for jails
        if 'startup_script' not in instance.config:
            instance.config['startup_script'] = path.join(
                ploy_path, 'startup-ansible-jail')
        if 'flavour' not in instance.config:
            instance.config['flavour'] = 'base'


def get_commands(aws):
    return [('bootstrap', PloyBootstrapCmd(aws))]


plugin = dict(
    augment_instance=augment_instance,
    get_commands=get_commands)


def ploy(configname=None, **kw):  # pragma: no cover
    from sys import argv
    if '-v' in argv:
        return version()
    if configname is None:
        configname = 'ploy.conf'
    return aws(configname=configname, progname='ploy', **kw)


def ploy_ssh(configname=None, **kw):  # pragma: no cover
    if configname is None:
        configname = 'ploy.conf'
    return aws_ssh(configname=configname, progname='ploy', **kw)


def version():
    for package in [
        'bsdploy',
        'mr.awsome',
        'mr.awsome.ansible',
        'mr.awsome.ezjail',
        'mr.awsome.fabric',
        ]:
        print('%s: %s' % (package, get_distribution(package).version))