from os import path
import argparse
import logging
import pkg_resources
import sys


log = logging.getLogger("bsdploy")


# register our own library and roles paths into ansible
ploy_path = pkg_resources.get_distribution("bsdploy").location
bsdploy_path = path.abspath(path.dirname(__file__))

ansible_paths = dict(
    roles=[path.join(ploy_path, 'roles')],
    library=[path.join(ploy_path, 'library')])


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
        args = parser.parse_args(argv)
        master = args.master if len(masters) == 1 else args.master[0]
        instance = self.ctrl.instances[master]
        instance.hooks.before_bsdploy_bootstrap(instance)
        instance.do('bootstrap')
        instance.hooks.after_bsdploy_bootstrap(instance)


def augment_instance(instance):
    from ploy_ansible import has_playbook
    if not instance.master.sectiongroupname.startswith('ez-'):
        return
    if 'ansible_python_interpreter' not in instance.config:
        instance.config['ansible_python_interpreter'] = '/usr/local/bin/python2.7'
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
    else:
        # for jails
        if 'startup_script' not in instance.config:
            instance.config['startup_script'] = path.join(
                bsdploy_path, 'startup-ansible-jail.sh')
        if 'flavour' not in instance.config:
            instance.config['flavour'] = 'base'


def get_commands(ctrl):
    return [('bootstrap', PloyBootstrapCmd(ctrl))]


plugin = dict(
    augment_instance=augment_instance,
    get_commands=get_commands)
