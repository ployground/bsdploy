from bsdploy import bsdploy_path
from fabric.api import env, quiet, run, settings
from lazy import lazy
from os.path import join, expanduser, exists, abspath
from ploy.common import yesno
try:  # pragma: nocover
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: nocover
    from yaml import SafeLoader
import os
import sys
import yaml


class BootstrapUtils:
    ssh_keys = frozenset([
        ('ssh_host_key', '-t rsa1 -b 1024'),
        ('ssh_host_rsa_key', '-t rsa'),
        ('ssh_host_dsa_key', '-t dsa'),
        ('ssh_host_ecdsa_key', '-t ecdsa')])
    upload_authorized_keys = True
    bootstrap_files_yaml = 'files.yml'

    @lazy
    def bootstrap_files(self):
        """ we need some files to bootstrap the FreeBSD installation.
        Some...
            - need to be provided by the user (i.e. authorized_keys)
            - others have some (sensible) defaults (i.e. rc.conf)
            - some can be downloaded via URL (i.e.) http://pkg.freebsd.org/freebsd:9:x86:64/latest/Latest/pkg.txz

        For those which can be downloaded we check the downloads directory. if the file exists there
        (and if the checksum matches TODO!) we will upload it to the host. If not, we will fetch the file
        from the given URL from the host.

        For files that cannot be downloaded (authorized_keys, rc.conf etc.) we allow the user to provide their
        own version in a ``bootstrap-files`` folder. The location of this folder can either be explicitly provided
        via the ``bootstrap-files`` key in the host definition of the config file or it defaults to ``deployment/bootstrap-files``.

        User provided files can be rendered as Jinja2 templates, by providing ``use_jinja: True`` in the YAML file.
        They will be rendered with the instance configuration dictionary as context.

        If the file is not found there, we revert to the default
        files that are part of bsdploy. If the file cannot be found there either we either error out or for authorized_keys
        we look in ``~/.ssh/identity.pub``.
        """
        ploy_conf_path = env.instance.master.main_config.path
        default_template_path = join(bsdploy_path, 'bootstrap-files')
        host_defined_path = env.instance.config.get('bootstrap-files')
        if host_defined_path is None:
            custom_template_path = abspath(join(ploy_conf_path, '..', 'deployment', 'bootstrap-files'))
        else:
            custom_template_path = abspath(join(ploy_conf_path, host_defined_path))
        download_path = abspath(join(ploy_conf_path, '..', 'downloads'))
        bootstrap_file_yamls = [
            abspath(join(default_template_path, self.bootstrap_files_yaml)),
            abspath(join(custom_template_path, self.bootstrap_files_yaml))]
        bootstrap_files = dict()
        if self.upload_authorized_keys:
            bootstrap_files['authorized_keys'] = {
                'directory': '/mnt/root/.ssh',
                'directory_mode': '0600',
                'remote': '/mnt/root/.ssh/authorized_keys',
                'expected_path': ploy_conf_path,
                'fallback': [
                    '~/.ssh/identity.pub',
                    '~/.ssh/id_rsa.pub',
                    '~/.ssh/id_dsa.pub',
                    '~/.ssh/id_ecdsa.pub']}
        for bootstrap_file_yaml in bootstrap_file_yamls:
            if not exists(bootstrap_file_yaml):
                continue
            with open(bootstrap_file_yaml) as f:
                info = yaml.load(f, Loader=SafeLoader)
            if info is None:
                continue
            bootstrap_files.update(info)

        for filename, info in bootstrap_files.items():
            if 'expected_path' in info:
                expected_path = info['expected_path']
            elif 'url' in info:
                expected_path = download_path
            else:
                expected_path = custom_template_path

            local_path = join(expected_path, filename)

            if not exists(local_path) and 'fallback' in info:
                local_paths = info['fallback']
                if isinstance(local_paths, basestring):
                    local_paths = [local_paths]
                local_paths = (expanduser(x) for x in local_paths)
                local_paths = [x for x in local_paths if exists(x)]
                if not local_paths:
                    print("Found no public key in %s, you have to create '%s' manually" % (expanduser('~/.ssh'), local_path))
                    sys.exit(1)
                print("The '%s' file is missing." % local_path)
                for path in sorted(local_paths):
                    if yesno("Should we generate it using the key in '%s'?" % path):
                        with open(local_path, 'wb') as out:
                            with open(path, 'rb') as f:
                                out.write(f.read())
                        break
                else:
                    # answered no to all options
                    sys.exit(1)

            if not exists(local_path) and 'url' not in info:
                local_path = join(default_template_path, filename)

            if not exists(local_path) and 'url' not in info:
                print('Cannot find %s' % local_path)
                sys.exit(1)

            bootstrap_files[filename]['local'] = local_path

        packages_path = join(download_path, 'packages')
        if exists(packages_path):
            for dirpath, dirnames, filenames in os.walk(packages_path):
                path = dirpath.split(packages_path)[1][1:]
                for filename in filenames:
                    if not filename.endswith('.txz'):
                        continue
                    bootstrap_files[join(path, filename)] = dict(
                        local=join(dirpath, filename),
                        remote=join('/mnt/var/cache/pkg/All', filename))

        if self.ssh_keys is not None:
            for ssh_key_name, ssh_key_options in list(self.ssh_keys):
                ssh_key = join(custom_template_path, ssh_key_name)
                if exists(ssh_key):
                    pub_key_name = '%s.pub' % ssh_key_name
                    pub_key = '%s.pub' % ssh_key
                    if not exists(pub_key):
                        print("Public key '%s' for '%s' missing." % (pub_key, ssh_key))
                        sys.exit(1)
                    bootstrap_files[ssh_key_name] = dict(local=ssh_key, remote='/mnt/etc/ssh/%s' % ssh_key_name, mode=0600)
                    bootstrap_files[pub_key_name] = dict(local=pub_key, remote='/mnt/etc/ssh/%s' % pub_key_name, mode=0644)
        return bootstrap_files

    @lazy
    def mounts(self):
        with settings(quiet()):
            return run('mount')

    @lazy
    def sysctl_devices(self):
        with settings(quiet()):
            return run('sysctl -n kern.disks').strip().split()

    @lazy
    def interfaces(self):
        with settings(quiet()):
            return run('ifconfig -l').strip().split()

    @lazy
    def phys_interfaces(self):
        return [x for x in self.interfaces if not x.startswith('lo')]

    @lazy
    def first_interface(self):
        if len(self.phys_interfaces):
            return self.phys_interfaces[0]

    @lazy
    def realmem(self):
        import math
        with settings(quiet()):
            realmem = run('sysctl -n hw.realmem').strip()
        realmem = float(realmem) / 1024 / 1024
        return 2 ** int(math.ceil(math.log(realmem, 2)))

    @lazy
    def install_devices(self):
        mounts = self.mounts
        with settings(quiet()):
            cd_device = env.instance.config.get('bootstrap-cd-device', 'cd0')
            if '/dev/{dev} on /rw/cdrom'.format(dev=cd_device) not in mounts:
                run('test -e /dev/{dev} && mount_cd9660 /dev/{dev} /cdrom || true'.format(dev=cd_device))
            usb_device = env.instance.config.get('bootstrap-usb-device', 'da0a')
            if '/dev/{dev} on /rw/media'.format(dev=usb_device) not in mounts:
                run('test -e /dev/{dev} && mount -o ro /dev/{dev} /media || true'.format(dev=usb_device))

        return [cd_device, usb_device]

    @lazy
    def devices(self):
        """ computes the name of the disk devices that are suitable
        installation targets by subtracting CDROM- and USB devices
        from the list of total mounts.
        """
        install_devices = self.install_devices
        if 'bootstrap-system-devices' in env.instance.config:
            devices = set(env.instance.config['bootstrap-system-devices'].split())
        else:
            devices = set(self.sysctl_devices)
            for sysctl_device in self.sysctl_devices:
                for install_device in install_devices:
                    if install_device.startswith(sysctl_device):
                        devices.remove(sysctl_device)
        return devices

    @lazy
    def bsd_url(self):
        bsd_url = env.instance.config.get('bootstrap-bsd-url')
        if not bsd_url:
            with settings(quiet(), warn_only=True):
                result = run("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \;")
                if result.return_code == 0:
                    bsd_url = result.strip()
        return bsd_url
