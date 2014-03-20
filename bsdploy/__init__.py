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


class PloyBootstrapCmd(object):

    def __init__(self, aws):
        self.aws = aws

    def __call__(self, argv, help):
        """Bootstrap a jailhost"""
        parser = argparse.ArgumentParser(
            prog="ploy bootstrap",
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

def get_commands(aws):
    return [
        ('bootstrap', PloyBootstrapCmd(aws))]


plugin = dict(
    get_commands=get_commands)
