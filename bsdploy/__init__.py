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