from __future__ import absolute_import, print_function
import os
import yaml
import sys
from bsdploy.bootstrap_utils import BootstrapUtils
from fabric.api import env, local
from os.path import join, exists, abspath, dirname
try:  # pragma: nocover
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: nocover
    from yaml import SafeLoader


def _fetch_packages(env, packagesite, packages):
    import tarfile
    try:
        import lzma
    except ImportError:
        print("ERROR: The lzma package couldn't be imported.")
        print("You most likely need to install pyliblzma in your virtualenv.")
        sys.exit(1)
    ploy_conf_path = join(env.instance.master.main_config.path)
    download_path = abspath(join(ploy_conf_path, '..', 'downloads'))
    packageinfo = {}
    print("Loading package information from '%s'." % packagesite)
    if SafeLoader.__name__ != 'CSafeLoader':
        print("WARNING: The C extensions for PyYAML aren't installed.")
        print("This can take quite a long while ...")
    else:
        print("This can take a while ...")
    for line in tarfile.TarFile(fileobj=lzma.LZMAFile(packagesite)).extractfile('packagesite.yaml'):
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
        items.append((
            join('packages', path),
            dict(
                url='http://pkg.freebsd.org/%s' % path,
                local=join(download_path, 'packages', path),
                remote=join('/mnt/var/cache/pkg/', info['path']))))
        seen.add(dep)
    return items


def fetch_assets(**kwargs):
    """ download bootstrap assets to control host.
    If present on the control host they will be uploaded to the target host during bootstrapping.
    """
    # allow overwrites from the commandline
    env.instance.config.update(kwargs)
    items = sorted(BootstrapUtils().bootstrap_files.items())
    packages = set(
        env.instance.config.get('bootstrap-packages', '').split())
    packages.update(['python27'])
    cmd = env.instance.config.get('bootstrap-local-download-cmd', 'wget -c -O {local} {url}')
    for filename, asset in items:
        if 'url' in asset:
            if not exists(dirname(asset['local'])):
                os.makedirs(dirname(asset['local']))
            local(cmd.format(**asset))
        if filename == 'packagesite.txz':
            items.extend(_fetch_packages(env, asset['local'], packages))
