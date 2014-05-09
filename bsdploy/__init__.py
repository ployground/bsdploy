import argparse
from mr.awsome import aws, aws_ssh
from os import path


# register our own library and roles paths into ansible
ploy_path = path.abspath(path.join(path.dirname(__file__), '../'))

ansible_paths = dict(
    roles=[path.join(ploy_path, 'roles')],
    library=[path.join(ploy_path, 'library')]
)


class PloyBootstrapHostCmd(object):

    def __init__(self, aws):
        self.aws = aws

    def __call__(self, argv, help):
        """Bootstrap a jailhost that's been booted into MFSBsd."""
        parser = argparse.ArgumentParser(
            prog="ploy bootstrap-jailhost",
            description=help,
            add_help=False,
        )
        masters = dict((master.id, master) for master in self.aws.get_masters('ezjail_admin'))
        if len(masters) > 1:
            parser.add_argument(
                "master",
                nargs=1,
                metavar="master",
                help="Name of the jailhost from the config.",
                choices=masters)
        args = parser.parse_args(argv)
        if len(masters) > 1:
            master = args.master[0]
        else:
            master = masters.keys()[0]
        instance = self.aws.instances[master]
        bootstrap_task = 'bootstrap'
        bootstrap_type = instance.config.get('bootstrap')
        if bootstrap_type:
            bootstrap_task = '%s_%s' % (bootstrap_task, bootstrap_type)
        if 'fabfile' not in instance.config:
            import os
            instance.config['fabfile'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fabfile.py')
        instance.do(bootstrap_task)


class PloyConfigureHostCmd(object):

    def __init__(self, aws):
        self.aws = aws

    def __call__(self, argv, help):
        """Configure a jailhost (installs ezjail etc.) after it has been bootstrapped."""
        parser = argparse.ArgumentParser(
            prog="ploy configure-jailhost",
            description=help,
            add_help=False,
        )
        masters = dict((master.id, master) for master in self.aws.get_masters('ezjail_admin'))
        if len(masters) > 1:
            parser.add_argument(
                "master",
                nargs=1,
                metavar="master",
                help="Name of the jailhost from the config.",
                choices=masters)
        args = parser.parse_args(argv)
        if len(masters) > 1:
            master = args.master[0]
        else:
            master = masters.keys()[0]
        instance = self.aws.instances[master]
        instance.apply_playbook(path.join(ploy_path, 'roles', 'jailhost.yml'), skip_host_check=True)


def get_commands(aws):
    return [
        ('bootstrap-jailhost', PloyBootstrapHostCmd(aws)),
        ('configure-jailhost', PloyConfigureHostCmd(aws))]


def get_massagers():
    from mr.awsome.config import HooksMassager
    return [HooksMassager('ez-instance', 'hooks')]


class AWSomeHooks(object):

    def before_start(self, server):
        """make sure we have a startup script for jails that installs python
        into it (so we can control it via ansible)
        """
        try:
            if not server.master.sectiongroupname.startswith('ez-'):
                return
        except AttributeError:
            return
        if 'startup_script' not in server.config:
            server.config['startup_script'] = path.join(ploy_path, 'startup-ansible-jail')


def get_hooks():
    return [AWSomeHooks()]


def get_ansible_vars(server):
    result = {}
    if server.master.sectiongroupname.startswith('ez-'):
        result['ansible_python_interpreter'] = '/usr/local/bin/python2.7'
    return result


plugin = dict(
    get_hooks=get_hooks,
    get_massagers=get_massagers,
    get_commands=get_commands,
    get_ansible_vars=get_ansible_vars)


def ploy(configname=None, **kw):  # pragma: no cover
    if configname is None:
        configname = 'ploy.conf'
    return aws(configname=configname, **kw)


def ploy_ssh(configname=None, **kw):  # pragma: no cover
    if configname is None:
        configname = 'ploy.conf'
    return aws_ssh(configname=configname, **kw)
