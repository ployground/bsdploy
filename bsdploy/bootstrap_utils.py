from __future__ import print_function
try:  # pragma: nocover
    from cStringIO import StringIO
except ImportError:  # pragma: nocover
    from StringIO import StringIO
from bsdploy import bsdploy_path
from fabric.api import env, local, put, quiet, run, settings
from lazy import lazy
from os.path import abspath, dirname, expanduser, exists, join
from ploy.common import yesno
try:  # pragma: nocover
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: nocover
    from yaml import SafeLoader
import os
import sys
import weakref
import yaml


class BootstrapFile(object):
    def __init__(self, bu, filename, **kwargs):
        self.bu = weakref.ref(bu)
        self.filename = filename
        self.info = kwargs
        self.info.setdefault('use_jinja', False)

    def __getattr__(self, name):
        return self.info.get(name)

    @property
    def expected_path(self):
        if 'url' in self.info:
            return self.bu().download_path
        else:
            return self.bu().custom_template_path

    @property
    def raw_fallback(self):
        paths = self.info.get('fallback', [])
        if isinstance(paths, basestring):
            paths = [paths]
        return paths

    @property
    def existing_fallback(self):
        paths = (expanduser(x) for x in self.raw_fallback)
        return sorted([x for x in paths if exists(x)])

    @property
    def local(self):
        if 'local' in self.info:
            return self.info['local']
        local_path = join(self.expected_path, self.filename)
        if self.raw_fallback:
            return local_path
        if not exists(local_path) and not self.url:
            local_path = join(self.bu().default_template_path, self.filename)
        if not exists(local_path) and not self.url:
            return
        return local_path

    def check(self):
        return exists(self.local) or self.url

    @property
    def to_be_fetched(self):
        return 'remote' in self.info and self.url and not exists(self.local)

    @lazy
    def template_from_file(self):
        from ploy_ansible import inject_ansible_paths
        inject_ansible_paths()
        from ansible.utils.template import template_from_file
        return template_from_file

    def open(self, context):
        if self.use_jinja:
            result = self.template_from_file(dirname(self.local), self.local, context)
            if isinstance(result, unicode):
                result = result.encode('utf-8')
            return StringIO(result)
        elif self.encrypted:
            vaultlib = env.instance.get_vault_lib()
            with open(self.local, 'r') as f:
                result = f.read()
            return StringIO(vaultlib.decrypt(result))
        else:
            return open(self.local, 'r')

    def read(self, context):
        return self.open(context).read()


class BootstrapUtils:
    ssh_keys = frozenset([
        ('ssh_host_rsa_key', '-t rsa'),
        ('ssh_host_dsa_key', '-t dsa'),
        ('ssh_host_ecdsa_key', '-t ecdsa'),
        ('ssh_host_ed25519_key', '-t ed25519')])
    upload_authorized_keys = True
    bootstrap_files_yaml = 'files.yml'

    @property
    def ploy_conf_path(self):
        return env.instance.master.main_config.path

    @property
    def default_template_path(self):
        return join(bsdploy_path, 'bootstrap-files')

    @property
    def custom_template_path(self):
        host_defined_path = env.instance.config.get('bootstrap-files')
        if host_defined_path is None:
            return abspath(join(self.ploy_conf_path, '..', 'bootstrap-files'))
        else:
            return abspath(join(self.ploy_conf_path, host_defined_path))

    @property
    def env_vars(self):
        env_vars = ''
        if env.instance.config.get('http_proxy'):
            env_vars = 'setenv http_proxy %s && ' % env.instance.config.get('http_proxy')
            env_vars += 'setenv https_proxy %s && ' % env.instance.config.get('http_proxy')
        return env_vars

    @property
    def download_path(self):
        return abspath(join(self.ploy_conf_path, '..', 'downloads'))

    def generate_ssh_keys(self):
        for ssh_key_name, ssh_keygen_args in sorted(self.ssh_keys):
            if not exists(self.custom_template_path):
                os.mkdir(self.custom_template_path)
            ssh_key = join(self.custom_template_path, ssh_key_name)
            if exists(ssh_key):
                continue
            with settings(quiet(), warn_only=True):
                result = local(
                    "ssh-keygen %s -f %s -N ''" % (ssh_keygen_args, ssh_key),
                    capture=True)
                if result.failed:
                    print("Generation of %s with '%s' failed." % (
                        ssh_key_name, ssh_keygen_args))
                    continue
            with settings(quiet()):
                fingerprint = local(
                    "ssh-keygen -lf %s" % ssh_key, capture=True).split()[1]
            print("Generated %s with fingerprint %s." % (ssh_key_name, fingerprint))

    def generate_remote_ssh_keys(self):
        for ssh_key, ssh_keygen_args in sorted(self.ssh_keys):
            if ssh_key not in self.bootstrap_files:
                run("ssh-keygen %s -f /mnt/etc/ssh/%s -N ''" % (ssh_keygen_args, ssh_key))

    @lazy
    def bootstrap_files(self):
        """ we need some files to bootstrap the FreeBSD installation.
        Some...
            - need to be provided by the user (i.e. authorized_keys)
            - others have some (sensible) defaults (i.e. rc.conf)
            - some can be downloaded via URL (i.e.) http://pkg.freebsd.org/freebsd:10:x86:64/latest/Latest/pkg.txz

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
        bootstrap_file_yamls = [
            abspath(join(self.default_template_path, self.bootstrap_files_yaml)),
            abspath(join(self.custom_template_path, self.bootstrap_files_yaml))]
        bootstrap_files = dict()
        if self.upload_authorized_keys:
            bootstrap_files['authorized_keys'] = BootstrapFile(self, 'authorized_keys', **{
                'directory': '/mnt/root/.ssh',
                'directory_mode': '0600',
                'remote': '/mnt/root/.ssh/authorized_keys',
                'fallback': [
                    '~/.ssh/identity.pub',
                    '~/.ssh/id_rsa.pub',
                    '~/.ssh/id_dsa.pub',
                    '~/.ssh/id_ecdsa.pub']})
        for bootstrap_file_yaml in bootstrap_file_yamls:
            if not exists(bootstrap_file_yaml):
                continue
            with open(bootstrap_file_yaml) as f:
                info = yaml.load(f, Loader=SafeLoader)
            if info is None:
                continue
            for k, v in info.items():
                bootstrap_files[k] = BootstrapFile(self, k, **v)

        for bf in bootstrap_files.values():
            if not exists(bf.local) and bf.raw_fallback:
                if not bf.existing_fallback:
                    print("Found no public key in %s, you have to create '%s' manually" % (expanduser('~/.ssh'), bf.local))
                    sys.exit(1)
                print("The '%s' file is missing." % bf.local)
                for path in bf.existing_fallback:
                    yes = env.instance.config.get('bootstrap-yes', False)
                    if yes or yesno("Should we generate it using the key in '%s'?" % path):
                        if not exists(bf.expected_path):
                            os.mkdir(bf.expected_path)
                        with open(bf.local, 'wb') as out:
                            with open(path, 'rb') as f:
                                out.write(f.read())
                        break
                else:
                    # answered no to all options
                    sys.exit(1)

            if not bf.check():
                print('Cannot find %s' % bf.local)
                sys.exit(1)

        packages_path = join(self.download_path, 'packages')
        if exists(packages_path):
            for dirpath, dirnames, filenames in os.walk(packages_path):
                path = dirpath.split(packages_path)[1][1:]
                for filename in filenames:
                    if not filename.endswith('.txz'):
                        continue
                    bootstrap_files[join(path, filename)] = BootstrapFile(
                        self, join(path, filename), **dict(
                            local=join(packages_path, join(path, filename)),
                            remote=join('/mnt/var/cache/pkg/All', filename),
                            encrypted=False))

        if self.ssh_keys is not None:
            for ssh_key_name, ssh_key_options in list(self.ssh_keys):
                ssh_key = join(self.custom_template_path, ssh_key_name)
                if exists(ssh_key):
                    pub_key_name = '%s.pub' % ssh_key_name
                    pub_key = '%s.pub' % ssh_key
                    if not exists(pub_key):
                        print("Public key '%s' for '%s' missing." % (pub_key, ssh_key))
                        sys.exit(1)
                    bootstrap_files[ssh_key_name] = BootstrapFile(
                        self, ssh_key_name, **dict(
                            local=ssh_key,
                            remote='/mnt/etc/ssh/%s' % ssh_key_name,
                            mode=0600))
                    bootstrap_files[pub_key_name] = BootstrapFile(
                        self, pub_key_name, **dict(
                            local=pub_key,
                            remote='/mnt/etc/ssh/%s' % pub_key_name,
                            mode=0644))
        if hasattr(env.instance, 'get_vault_lib'):
            vaultlib = env.instance.get_vault_lib()
            for bf in bootstrap_files.values():
                if bf.encrypted is None and exists(bf.local):
                    with open(bf.local) as f:
                        data = f.read()
                    bf.info['encrypted'] = vaultlib.is_encrypted(data)
        return bootstrap_files

    def print_bootstrap_files(self):
        print("\nUsing these local files for bootstrapping:")
        for filename, bf in sorted(self.bootstrap_files.items()):
            if not bf.to_be_fetched:
                print('{0.local} -(template:{0.use_jinja})-> {0.remote}'.format(bf))
        to_be_fetched_count = 0
        for filename, bf in sorted(self.bootstrap_files.items()):
            if bf.to_be_fetched:
                if to_be_fetched_count == 0:
                    print("\nThe following files will be downloaded on the host during bootstrap:")
                    if env.instance.config.get('http_proxy'):
                        print("\nUsing http proxy {http_proxy}".format(**env.instance.config))
                to_be_fetched_count += 1
                print('{0.url} -> {0.remote}'.format(bf))
        if to_be_fetched_count == 0:
            print("\nNo files will be downloaded on the host during bootstrap.")
        print()

    def create_bootstrap_directories(self):
        for filename, bf in sorted(self.bootstrap_files.items()):
            if not bf.directory:
                continue
            cmd = 'mkdir -p "%s"' % bf.directory
            if bf.directory_mode:
                cmd = '%s && chmod %s "%s"' % (cmd, bf.directory_mode, bf.directory)
            run(cmd, shell=False)

    def upload_bootstrap_files(self, context):
        for filename, bf in sorted(self.bootstrap_files.items()):
            if bf.remote and exists(bf.local):
                put(bf.open(context), bf.remote, mode=bf.mode)

    def install_pkg(self, root, chroot=None, packages=[]):
        assert isinstance(chroot, bool)
        chroot_prefix = 'chroot %s ' % root if chroot else ''

        pkg = self.bootstrap_files.get('pkg.txz')
        if pkg is not None:
            print("\nInstalling pkg")
            if not exists(pkg.local):
                run(self.env_vars + 'fetch -o {0.remote} {0.url}'.format(pkg), shell=False)
            run('chmod 0600 {0.remote}'.format(pkg))
            run("tar -x -C {root}{chroot} --exclude '+*' -f {0.remote}".format(
                pkg, root=root, chroot=' --chroot' if chroot else ''))
            # run pkg2ng for which the shared library path needs to be updated
            run(chroot_prefix + '/etc/rc.d/ldconfig start')
            run(chroot_prefix + 'pkg2ng')

        run(self.env_vars + chroot_prefix + 'pkg update', shell=False)

        if packages:
            run(self.env_vars + chroot_prefix + 'pkg install %s' % ' '.join(packages), shell=False)

    @lazy
    def mounts(self):
        with settings(quiet()):
            return run('mount')

    @lazy
    def os_release(self):
        with settings(quiet()):
            return run('uname -r')

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
        # make sure the devices are mounted
        self.install_devices
        bsd_url = env.instance.config.get('bootstrap-bsd-url')
        if not bsd_url:
            with settings(quiet(), warn_only=True):
                result = run("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \;")
                if result.return_code == 0:
                    bsd_url = result.strip()
        return bsd_url

    @lazy
    def zfsinstall(self):
        zfsinstall = env.instance.config.get('bootstrap-zfsinstall')
        if zfsinstall:
            dest = '/root/bin/bsdploy_zfsinstall'
            put(abspath(join(self.ploy_conf_path, zfsinstall)), dest, mode=0755)
            return dest
        else:
            return 'zfsinstall'

    def _fetch_packages(self, packagesite, packages):
        import tarfile
        try:
            import lzma
        except ImportError:
            print("ERROR: The lzma package couldn't be imported.")
            print("You most likely need to install pyliblzma in your virtualenv.")
            sys.exit(1)
        packageinfo = {}
        print("Loading package information from '%s'." % packagesite)
        if SafeLoader.__name__ != 'CSafeLoader':
            print("WARNING: The C extensions for PyYAML aren't installed.")
            print("This can take quite a long while ...")
        else:
            print("This can take a while ...")
        packagesite_yaml = tarfile.TarFile(
            fileobj=lzma.LZMAFile(packagesite)).extractfile('packagesite.yaml')
        for line in packagesite_yaml:
            info = yaml.load(line, Loader=SafeLoader)
            packageinfo[info['name']] = dict(
                path=info['path'],
                arch=info['arch'],
                deps=info.get('deps', {}).keys())
        deps = set(packages)
        seen = set()
        items = []
        while 1:
            try:
                dep = deps.pop()
            except KeyError:
                break
            if dep in seen:
                continue
            info = packageinfo[dep]
            deps.update(info['deps'])
            path = '%s/latest/%s' % (info['arch'], info['path'])
            filename = join('packages', path)
            items.append((
                filename,
                BootstrapFile(
                    self, filename,
                    url='http://pkg.freebsd.org/%s' % path,
                    local=join(self.download_path, 'packages', path),
                    remote=join('/mnt/var/cache/pkg/', info['path']))))
            seen.add(dep)
        return items

    def fetch_assets(self):
        """ download bootstrap assets to control host.
        If present on the control host they will be uploaded to the target host during bootstrapping.
        """
        # allow overwrites from the commandline
        packages = set(
            env.instance.config.get('bootstrap-packages', '').split())
        packages.update(['python27'])
        cmd = env.instance.config.get('bootstrap-local-download-cmd', 'wget -c -O "{0.local}" "{0.url}"')
        items = sorted(self.bootstrap_files.items())
        for filename, asset in items:
            if asset.url:
                if not exists(dirname(asset.local)):
                    os.makedirs(dirname(asset.local))
                local(cmd.format(asset))
            if filename == 'packagesite.txz':
                # add packages to download
                items.extend(self._fetch_packages(asset.local, packages))
