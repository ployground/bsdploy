from fabric.api import env, sudo
from fabric.contrib.project import rsync_project as _rsync_project
from ploy.common import shjoin


def rsync_project(*args, **kwargs):
    ssh_info = env.instance.init_ssh_key()
    ssh_info.pop('host')
    ssh_args = env.instance.ssh_args_from_info(ssh_info)
    kwargs['ssh_opts'] = '%s %s' % (kwargs.get('ssh_opts', ''), shjoin(ssh_args))
    with env.instance.fabric():
        env.host_string = "{user}@{host}".format(
            user=env.instance.config.get('user', 'root'),
            host=env.instance.config.get(
                'host', env.instance.config.get(
                    'ip', env.instance.uid)))
        _rsync_project(*args, **kwargs)


def service(service=None, action='status'):
    if service is None:
        exit("You must provide a service name")
    sudo('service %s %s' % (service, action), warn_only=True)
