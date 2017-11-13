from bsdploy import bsdploy_path
from bsdploy.tests.conftest import default_mounts, run_result
import pytest


@pytest.fixture
def bootstrap(env_mock, environ_mock, monkeypatch, put_mock, run_mock, tempdir, yesno_mock, ployconf):
    from bsdploy.fabfile_mfsbsd import bootstrap
    ployconf.fill('')
    environ_mock['HOME'] = tempdir.directory
    monkeypatch.setattr('bsdploy.fabfile_mfsbsd.env', env_mock)
    monkeypatch.setattr('bsdploy.fabfile_mfsbsd.run', run_mock)
    monkeypatch.setattr('bsdploy.fabfile_mfsbsd.yesno', yesno_mock)
    return bootstrap


def create_ssh_host_keys(tempdir):
    tempdir['bootstrap-files/ssh_host_dsa_key'].fill('dsa')
    tempdir['bootstrap-files/ssh_host_dsa_key.pub'].fill('dsa.pub')
    tempdir['bootstrap-files/ssh_host_ecdsa_key'].fill('ecdsa')
    tempdir['bootstrap-files/ssh_host_ecdsa_key.pub'].fill('ecdsa.pub')
    tempdir['bootstrap-files/ssh_host_ed25519_key'].fill('ed25519')
    tempdir['bootstrap-files/ssh_host_ed25519_key.pub'].fill('ed25519.pub')
    tempdir['bootstrap-files/ssh_host_rsa_key'].fill('rsa')
    tempdir['bootstrap-files/ssh_host_rsa_key.pub'].fill('rsa.pub')


def test_bootstrap_ask_to_continue(bootstrap, capsys, run_mock, tempdir, yesno_mock):
    format_info = dict(
        bsdploy_path=bsdploy_path,
        tempdir=tempdir.directory)
    tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
    create_ssh_host_keys(tempdir)
    run_mock.expected = [
        ('mount', {}, default_mounts),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n'),
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('/cdrom/9.2-RELEASE-amd64', 0)),
        ('sysctl -n hw.realmem', {}, '536805376'),
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('ifconfig -l', {}, 'em0 lo0')]
    yesno_mock.expected = [
        ("\nContinuing will destroy the existing data on the following devices:\n    ada0\n\nContinue?", False)]
    bootstrap()
    (out, err) = capsys.readouterr()
    out_lines = out.splitlines()
    assert out_lines == [
        "",
        "Using these local files for bootstrapping:",
        "%(bsdploy_path)s/bootstrap-files/FreeBSD.conf -(template:True)-> /mnt/usr/local/etc/pkg/repos/FreeBSD.conf" % format_info,
        "%(tempdir)s/bootstrap-files/authorized_keys -(template:False)-> /mnt/root/.ssh/authorized_keys" % format_info,
        "%(bsdploy_path)s/bootstrap-files/make.conf -(template:False)-> /mnt/etc/make.conf" % format_info,
        "%(bsdploy_path)s/bootstrap-files/pf.conf -(template:False)-> /mnt/etc/pf.conf" % format_info,
        "%(bsdploy_path)s/bootstrap-files/pkg.conf -(template:True)-> /mnt/usr/local/etc/pkg.conf" % format_info,
        "%(bsdploy_path)s/bootstrap-files/rc.conf -(template:True)-> /mnt/etc/rc.conf" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_dsa_key -(template:False)-> /mnt/etc/ssh/ssh_host_dsa_key" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_dsa_key.pub -(template:False)-> /mnt/etc/ssh/ssh_host_dsa_key.pub" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_ecdsa_key -(template:False)-> /mnt/etc/ssh/ssh_host_ecdsa_key" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_ecdsa_key.pub -(template:False)-> /mnt/etc/ssh/ssh_host_ecdsa_key.pub" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_ed25519_key -(template:False)-> /mnt/etc/ssh/ssh_host_ed25519_key" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_ed25519_key.pub -(template:False)-> /mnt/etc/ssh/ssh_host_ed25519_key.pub" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_rsa_key -(template:False)-> /mnt/etc/ssh/ssh_host_rsa_key" % format_info,
        "%(tempdir)s/bootstrap-files/ssh_host_rsa_key.pub -(template:False)-> /mnt/etc/ssh/ssh_host_rsa_key.pub" % format_info,
        "%(bsdploy_path)s/bootstrap-files/sshd_config -(template:False)-> /mnt/etc/ssh/sshd_config" % format_info,
        "",
        "No files will be downloaded on the host during bootstrap.",
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


def test_bootstrap_no_newline_at_end_of_rc_conf(bootstrap, capsys, local_mock, run_mock, tempdir):
    tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
    create_ssh_host_keys(tempdir)
    tempdir['bootstrap-files/rc.conf'].fill('foo')
    run_mock.expected = [
        ('mount', {}, default_mounts),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n'),
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('/cdrom/9.2-RELEASE-amd64', 0)),
        ('sysctl -n hw.realmem', {}, '536805376'),
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('ifconfig -l', {}, 'em0 lo0')]
    bootstrap()
    (out, err) = capsys.readouterr()
    out_lines = out.splitlines()
    assert out_lines[-4:] == [
        "ERROR! Your rc.conf doesn't end in a newline:",
        '==========',
        'foo<<<<<<<<<<',
        '']


def test_bootstrap(bootstrap, put_mock, run_mock, tempdir, yesno_mock):
    format_info = dict(
        bsdploy_path=bsdploy_path,
        tempdir=tempdir.directory)
    tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
    create_ssh_host_keys(tempdir)
    put_mock.expected = [
        ((object, '/mnt/usr/local/etc/pkg/repos/FreeBSD.conf'), {'mode': None}),
        (("%(tempdir)s/bootstrap-files/authorized_keys" % format_info, '/mnt/root/.ssh/authorized_keys'), {'mode': None}),
        (("%(bsdploy_path)s/bootstrap-files/make.conf" % format_info, '/mnt/etc/make.conf'), {'mode': None}),
        # put from upload_template
        ((object, '/mnt/etc/pf.conf'), {'mode': None}),
        ((object, '/mnt/usr/local/etc/pkg.conf'), {'mode': None}),
        ((object, '/mnt/etc/rc.conf'), {'mode': None}),
        (("%(tempdir)s/bootstrap-files/ssh_host_dsa_key" % format_info, '/mnt/etc/ssh/ssh_host_dsa_key'), {'mode': 0600}),
        (("%(tempdir)s/bootstrap-files/ssh_host_dsa_key.pub" % format_info, '/mnt/etc/ssh/ssh_host_dsa_key.pub'), {'mode': 0644}),
        (("%(tempdir)s/bootstrap-files/ssh_host_ecdsa_key" % format_info, '/mnt/etc/ssh/ssh_host_ecdsa_key'), {'mode': 0600}),
        (("%(tempdir)s/bootstrap-files/ssh_host_ecdsa_key.pub" % format_info, '/mnt/etc/ssh/ssh_host_ecdsa_key.pub'), {'mode': 0644}),
        (("%(tempdir)s/bootstrap-files/ssh_host_ed25519_key" % format_info, '/mnt/etc/ssh/ssh_host_ed25519_key'), {'mode': 0600}),
        (("%(tempdir)s/bootstrap-files/ssh_host_ed25519_key.pub" % format_info, '/mnt/etc/ssh/ssh_host_ed25519_key.pub'), {'mode': 0644}),
        (("%(tempdir)s/bootstrap-files/ssh_host_rsa_key" % format_info, '/mnt/etc/ssh/ssh_host_rsa_key'), {'mode': 0600}),
        (("%(tempdir)s/bootstrap-files/ssh_host_rsa_key.pub" % format_info, '/mnt/etc/ssh/ssh_host_rsa_key.pub'), {'mode': 0644}),
        (("%(bsdploy_path)s/bootstrap-files/sshd_config" % format_info, '/mnt/etc/ssh/sshd_config'), {'mode': None}),
    ]
    run_mock.expected = [
        ('mount', {}, default_mounts),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n'),
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('/cdrom/9.2-RELEASE-amd64', 0)),
        ('sysctl -n hw.realmem', {}, '536805376'),
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('ifconfig -l', {}, 'em0 lo0'),
        ('destroygeom -d ada0 -p system -p tank', {}, ''),
        ('zfsinstall -d ada0 -p system -V 28 -u /cdrom/9.2-RELEASE-amd64 -s 1024M -z 20G', {'shell': False}, ''),
        ('gpart add -t freebsd-zfs -l tank_ada0 ada0', {}, ''),
        ('cp /etc/resolv.conf /mnt/etc/resolv.conf', {'warn_only': True}, ''),
        ('mkdir -p "/mnt/usr/local/etc/pkg/repos"', {'shell': False}, ''),
        ('mkdir -p "/mnt/root/.ssh" && chmod 0600 "/mnt/root/.ssh"', {'shell': False}, ''),
        ('chroot /mnt pkg update', {'shell': False}, ''),
        ('chroot /mnt pkg install python27', {'shell': False}, ''),
        ('echo autoboot_delay=-1 >> /mnt/boot/loader.conf', {}, ''),
        ('reboot', {}, '')]
    yesno_mock.expected = [
        ("\nContinuing will destroy the existing data on the following devices:\n    ada0\n\nContinue?", True)]
    bootstrap()
