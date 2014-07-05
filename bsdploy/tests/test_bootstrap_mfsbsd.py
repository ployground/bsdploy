from bsdploy import bsdploy_path
from bsdploy.tests.conftest import default_mounts, run_result
import pytest


@pytest.fixture
def bootstrap(env_mock, environ_mock, put_mock, run_mock, tempdir, yesno_mock, ployconf):
    from bsdploy.fabfile_mfsbsd import bootstrap
    ployconf.fill('')
    environ_mock['HOME'] = tempdir.directory
    return bootstrap


def test_bootstrap_ask_to_continue(bootstrap, capsys, run_mock, tempdir, yesno_mock):
    format_info = dict(
        bsdploy_path=bsdploy_path,
        tempdir=tempdir.directory)
    tempdir['etc/authorized_keys'].fill('id_dsa')
    run_mock.expected = [
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('/cdrom/9.2-RELEASE-amd64', 0)),
        ('sysctl -n hw.realmem', {}, '536805376'),
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('ifconfig -l', {}, 'em0 lo0'),
        ('mount', {}, default_mounts),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    yesno_mock.expected = [
        ("\nContinuing will destroy the existing data on the following devices:\n    ada0\n\nContinue?", False)]
    bootstrap()
    (out, err) = capsys.readouterr()
    out_lines = out.splitlines()
    assert out_lines == [
        "",
        "Using these local files for bootstrapping:",
        "%(bsdploy_path)s/bootstrap-files/FreeBSD.conf -(template:False)-> /mnt/usr/local/etc/pkg/repos/FreeBSD.conf" % format_info,
        "%(tempdir)s/etc/authorized_keys -(template:False)-> /mnt/root/.ssh/authorized_keys" % format_info,
        "%(bsdploy_path)s/bootstrap-files/make.conf -(template:False)-> /mnt/etc/make.conf" % format_info,
        "%(bsdploy_path)s/bootstrap-files/pkg.conf -(template:False)-> /mnt/usr/local/etc/pkg.conf" % format_info,
        "%(bsdploy_path)s/bootstrap-files/rc.conf -(template:True)-> /mnt/etc/rc.conf" % format_info,
        "%(bsdploy_path)s/bootstrap-files/sshd_config -(template:False)-> /mnt/etc/ssh/sshd_config" % format_info,
        "",
        "The following files will be downloaded on the host during bootstrap:",
        "http://pkg.freebsd.org/freebsd:9:x86:64/quarterly/Latest/pkg.txz -> /mnt/var/cache/pkg/All/pkg.txz",
        "",
        "",
        "Found the following disk devices on the system:",
        "    ada0 cd0",
        "",
        "Found the following network interfaces, now is your chance to update your rc.conf accordingly!",
        "    em0",
        "",
        "Continuing will destroy the existing data on the following devices:",
        "    ada0",
        "",
        "Continue?"]
