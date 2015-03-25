from ansible.errors import AnsibleUndefinedVariable
from bsdploy import bootstrap_utils
from bsdploy.tests.conftest import default_mounts, run_result
import os
import pytest


@pytest.fixture
def bu(env_mock, environ_mock, run_mock, ployconf, tempdir):
    ployconf.fill('')
    environ_mock['HOME'] = tempdir.directory
    return bootstrap_utils.BootstrapUtils()


def test_realmem(bu, run_mock):
    run_mock.expected = [('sysctl -n hw.realmem', {}, '536805376')]
    assert bu.realmem == 512


def test_interfaces(bu, run_mock):
    run_mock.expected = [('ifconfig -l', {}, 'em0 em1 lo0 lo1')]
    assert bu.first_interface == 'em0'
    assert bu.phys_interfaces == ['em0', 'em1']


def test_interfaces_missing(bu, run_mock):
    run_mock.expected = [('ifconfig -l', {}, 'lo0 lo1')]
    assert bu.first_interface is None
    assert bu.phys_interfaces == []


def test_devices(bu, run_mock):
    run_mock.expected = [
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('mount', {}, default_mounts),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    assert bu.sysctl_devices == ['ada0', 'cd0']
    assert bu.devices == set(['ada0'])


def test_devices_cdrom_mounted(bu, run_mock):
    run_mock.expected = [
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('mount', {}, '\n'.join([
            default_mounts,
            '/dev/cd0 on /rw/cdrom (cd9660, local, read-only)'])),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    assert bu.sysctl_devices == ['ada0', 'cd0']
    assert bu.devices == set(['ada0'])


def test_devices_usb_mounted(bu, run_mock):
    run_mock.expected = [
        ('sysctl -n kern.disks', {}, 'ada0 da0\n'),
        ('mount', {}, '\n'.join([
            default_mounts,
            '/dev/da0a on /rw/media (ufs, local, read-only)'])),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n')]
    assert bu.sysctl_devices == ['ada0', 'da0']
    assert bu.devices == set(['ada0'])


def test_devices_different_cdrom(bu, run_mock, env_mock):
    run_mock.expected = [
        ('sysctl -n kern.disks', {}, 'ada0 cd1\n'),
        ('mount', {}, default_mounts),
        ('test -e /dev/cd1 && mount_cd9660 /dev/cd1 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    env_mock.instance.config = {'bootstrap-cd-device': 'cd1'}
    assert bu.sysctl_devices == ['ada0', 'cd1']
    assert bu.devices == set(['ada0'])


def test_devices_different_usb(bu, run_mock, env_mock):
    run_mock.expected = [
        ('sysctl -n kern.disks', {}, 'ada0 cd0 da1\n'),
        ('mount', {}, default_mounts),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da1a && mount -o ro /dev/da1a /media || true', {}, '\n')]
    env_mock.instance.config = {'bootstrap-usb-device': 'da1a'}
    assert bu.sysctl_devices == ['ada0', 'cd0', 'da1']
    assert bu.devices == set(['ada0'])


def test_devices_from_config(bu, run_mock, env_mock):
    env_mock.instance.config = {'bootstrap-system-devices': 'ada0'}
    run_mock.expected = [
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('mount', {}, default_mounts),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    assert bu.sysctl_devices == ['ada0', 'cd0']
    assert bu.devices == set(['ada0'])


def test_bsd_url(bu, run_mock):
    run_mock.expected = [
        ('mount', {}, ''),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n'),
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('/cdrom/9.2-RELEASE-amd64', 0))]
    assert bu.bsd_url == '/cdrom/9.2-RELEASE-amd64'


def test_bsd_url_not_found(bu, run_mock):
    run_mock.expected = [
        ('mount', {}, ''),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n'),
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('', 1))]
    assert bu.bsd_url is None


def test_bsd_url_from_config(bu, env_mock, run_mock):
    env_mock.instance.config = {'bootstrap-bsd-url': '/foo'}
    run_mock.expected = [
        ('mount', {}, ''),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    assert bu.bsd_url == '/foo'


def test_bootstrap_files_no_ssh_keys(bu, capsys, tempdir):
    format_info = dict(tempdir=tempdir.directory)
    with pytest.raises(SystemExit) as e:
        bu.bootstrap_files
    assert e.value.code == 1
    (out, err) = capsys.readouterr()
    out_lines = out.splitlines()
    assert out_lines == [
        "Found no public key in %(tempdir)s/.ssh, you have to create '%(tempdir)s/bootstrap-files/authorized_keys' manually" % format_info]


def test_bootstrap_files_multiple_ssh_keys_but_none_used(bu, capsys, tempdir, yesno_mock):
    format_info = dict(tempdir=tempdir.directory)
    tempdir['.ssh/id_dsa.pub'].fill('id_dsa')
    tempdir['.ssh/id_rsa.pub'].fill('id_rsa')
    yesno_mock.expected = [
        ("Should we generate it using the key in '%(tempdir)s/.ssh/id_dsa.pub'?" % format_info, False),
        ("Should we generate it using the key in '%(tempdir)s/.ssh/id_rsa.pub'?" % format_info, False)]
    with pytest.raises(SystemExit) as e:
        bu.bootstrap_files()
    assert e.value.code == 1
    (out, err) = capsys.readouterr()
    out_lines = out.splitlines()
    assert out_lines == [
        "The '%(tempdir)s/bootstrap-files/authorized_keys' file is missing." % format_info,
        "Should we generate it using the key in '%(tempdir)s/.ssh/id_dsa.pub'?" % format_info,
        "Should we generate it using the key in '%(tempdir)s/.ssh/id_rsa.pub'?" % format_info]


def test_bootstrap_files_multiple_ssh_keys_use_second(bu, capsys, run_mock, tempdir, yesno_mock):
    format_info = dict(tempdir=tempdir.directory)
    tempdir['.ssh/id_dsa.pub'].fill('id_dsa')
    tempdir['.ssh/id_rsa.pub'].fill('id_rsa')
    yesno_mock.expected = [
        ("Should we generate it using the key in '%(tempdir)s/.ssh/id_dsa.pub'?" % format_info, False),
        ("Should we generate it using the key in '%(tempdir)s/.ssh/id_rsa.pub'?" % format_info, True)]
    bu.bootstrap_files
    (out, err) = capsys.readouterr()
    out_lines = out.splitlines()
    assert out_lines == [
        "The '%(tempdir)s/bootstrap-files/authorized_keys' file is missing." % format_info,
        "Should we generate it using the key in '%(tempdir)s/.ssh/id_dsa.pub'?" % format_info,
        "Should we generate it using the key in '%(tempdir)s/.ssh/id_rsa.pub'?" % format_info]
    assert os.path.exists(tempdir['bootstrap-files/authorized_keys'].path)
    with open(tempdir['bootstrap-files/authorized_keys'].path) as f:
        assert f.read() == 'id_rsa'


class TestFileEncryption:
    @pytest.fixture
    def ctrl(self, ctrl):
        import ploy_ansible
        ctrl.plugins['ansible'] = ploy_ansible.plugin
        return ctrl

    @pytest.fixture
    def passwd_source(self, monkeypatch):
        class DummySource:
            passwd = 'dummy-vault-password'

            def get(self, fail_on_error=True):
                return self.passwd
        src = DummySource()
        monkeypatch.setattr('ploy_ansible.get_vault_password_source', lambda x: src)
        return src

    def test_bootstrap_files_encrypted(self, bu, env_mock, passwd_source, tempdir):
        vaultlib = env_mock.instance.get_vault_lib()
        tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
        tempdir['bootstrap-files/secret.txt'].fill(vaultlib.encrypt('test-secret'))
        bindata = ''.join(chr(x) for x in range(256))
        tempdir['bootstrap-files/secret.bin'].fill(vaultlib.encrypt(bindata))
        with open(tempdir['bootstrap-files/secret.txt'].path) as f:
            assert 'test-secret' not in f.read()
        tempdir['bootstrap-files/files.yml'].fill([
            "'secret.txt':",
            "    remote: /root/secret.txt"])
        for name, bf in bu.bootstrap_files.items():
            if name == 'secret.txt':
                assert bf.encrypted
                assert bf.open({}).read() == 'test-secret'
            elif name == 'secret.bin':
                assert bf.encrypted
                assert bf.open({}).read() == bindata
            else:
                assert not bf.encrypted


def test_default_rc_conf(bu, tempdir):
    tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
    bfs = bu.bootstrap_files
    result = bfs['rc.conf'].read({
        'hostname': 'foo',
        'interfaces': []})
    assert result == '\n'.join([
        'hostname="foo"',
        'sshd_enable="YES"',
        'syslogd_flags="-ss"',
        'zfs_enable="YES"',
        'pf_enable="YES"',
        ''])


@pytest.mark.parametrize("input, context, expected", [
    ('foo', {}, 'foo'),
    ('{{ foo }}', {}, AnsibleUndefinedVariable),
    ('{{ foo }}', {'foo': 'bar'}, 'bar'),
    ('    {% for x in xs %}bar\nfoo_{{x}}\n{% endfor %}\n', {'xs': []}, '    \n'),
    ('    {% for x in xs %}bar\nfoo_{{x}}\n{% endfor %}\n', {'xs': ['bar']}, '    bar\nfoo_bar\n'),
    ('    {% for x in xs -%}\nfoo_{{x}}\n{% endfor %}\n', {'xs': ['bar']}, '    foo_bar\n'),
    ('    {% for x in xs %}bar\n    foo_{{x}}\n{% endfor %}\n', {'xs': []}, '    \n'),
    ('    {% for x in xs %}bar\n    foo_{{x}}\n{% endfor %}\n', {'xs': ['bar']}, '    bar\n    foo_bar\n'),
    ('    {% for x in xs -%}\n    foo_{{x}}\n{% endfor %}\n', {'xs': ['bar']}, '    foo_bar\n'),
])
def test_bootstrap_files_template(bu, input, context, expected, tempdir):
    tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
    tempdir['bootstrap-files/rc.conf'].fill(input)
    bfs = bu.bootstrap_files
    if isinstance(expected, basestring):
        result = bfs['rc.conf'].read(context)
        assert result == expected
        assert not isinstance(result, unicode)
    else:
        with pytest.raises(expected):
            bfs['rc.conf'].read(context)


def test_fetch_assets(bu, local_mock, tempdir):
    format_info = dict(tempdir=tempdir.directory)
    tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
    local_mock.expected = [
        ('wget -c -O "%(tempdir)s/downloads/pkg.txz" "http://pkg.freebsd.org/freebsd:10:x86:64/quarterly/Latest/pkg.txz"' % format_info, {}, '')]
    bu.fetch_assets()


def test_fetch_assets_packagesite(bu, local_mock, tempdir):
    from bsdploy import bsdploy_path
    pytest.importorskip("lzma")
    format_info = dict(tempdir=tempdir.directory)
    tempdir['bootstrap-files/authorized_keys'].fill('id_dsa')
    tempdir['bootstrap-files/files.yml'].fill([
        "'packagesite.txz':",
        "    url: 'http://pkg.freebsd.org/freebsd:10:x86:64/quarterly/packagesite.txz'",
        "    remote: '/mnt/var/cache/pkg/packagesite.txz'"])
    with open(os.path.join(bsdploy_path, 'tests', 'packagesite.txz')) as f:
        tempdir['downloads/packagesite.txz'].fill(f.read())
    local_mock.expected = [
        ('wget -c -O "%(tempdir)s/downloads/packagesite.txz" "http://pkg.freebsd.org/freebsd:10:x86:64/quarterly/packagesite.txz"' % format_info, {}, ''),
        ('wget -c -O "%(tempdir)s/downloads/packages/freebsd:10:x86:64/latest/All/python27-2.7.6_4.txz" "http://pkg.freebsd.org/freebsd:10:x86:64/latest/All/python27-2.7.6_4.txz"' % format_info, {}, ''),
        ('wget -c -O "%(tempdir)s/downloads/packages/freebsd:10:x86:64/latest/All/gettext-0.18.3.1.txz" "http://pkg.freebsd.org/freebsd:10:x86:64/latest/All/gettext-0.18.3.1.txz"' % format_info, {}, ''),
        ('wget -c -O "%(tempdir)s/downloads/packages/freebsd:10:x86:64/latest/All/libiconv-1.14_3.txz" "http://pkg.freebsd.org/freebsd:10:x86:64/latest/All/libiconv-1.14_3.txz"' % format_info, {}, '')]
    bu.fetch_assets()
