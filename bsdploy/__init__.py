import argparse
from mr.awsome import aws, aws_ssh
from os import path

def main(**kw):
    return aws(configname='ploy.conf', **kw)

def ssh(**kw):  # pragma: no cover
    return aws_ssh(configname='ploy.conf', **kw)

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
        parser.add_argument(
            "master",
            nargs=1,
            metavar="master",
            help="Name of the jailhost from the config.",
            choices=masters)
        args = parser.parse_args(argv[:1])
        instance = self.aws.instances[args.master[0]]
        instance.do('bootstrap')


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
        parser.add_argument(
            "master",
            nargs=1,
            metavar="master",
            help="Name of the jailhost from the config.",
            choices=masters)
        args = parser.parse_args(argv[:1])
        instance = self.aws.instances[args.master[0]]
        instance.apply_playbook(path.join(ploy_path, 'roles', 'jailhost.yml'))

def get_commands(aws):
    return [
        ('bootstrap-jailhost', PloyBootstrapHostCmd(aws)),
        ('configure-jailhost', PloyConfigureHostCmd(aws)),
        ]

def get_massagers():
    from mr.awsome.config import HooksMassager
    return [HooksMassager('ez-instance', 'hooks')]

plugin = dict(
    get_massagers=get_massagers,
    get_commands=get_commands)


class AWSomeHooks(object):

    def before_start(self, server):
        """make sure we have a startup script for jails that installs python
        into it (so we can control it via ansible)
        """
        if 'startup_script' not in server.config:
            server.config['startup_script'] = path.join(ploy_path, 'startup-ansible-jail')



