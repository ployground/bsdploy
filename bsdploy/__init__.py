from mr.awsome import aws, aws_ssh

def main(**kw):
	return aws(configname='ploy.conf', **kw)

def ssh(**kw):  # pragma: no cover
    return aws_ssh(configname='ploy.conf', **kw)
