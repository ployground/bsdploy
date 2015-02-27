from bsdploy import bsdploy_path
import pytest


@pytest.fixture
def bootstrap(env_mock, environ_mock, monkeypatch, put_mock, run_mock, tempdir, yesno_mock, ployconf):
    from bsdploy.fabfile_daemonology import bootstrap
    ployconf.fill('')
    environ_mock['HOME'] = tempdir.directory
    env_mock.host_string = 'jailhost'
    monkeypatch.setattr('bsdploy.fabfile_daemonology.env', env_mock)
    monkeypatch.setattr('bsdploy.fabfile_daemonology.put', put_mock)
    monkeypatch.setattr('bsdploy.fabfile_daemonology.run', run_mock)
    monkeypatch.setattr('bsdploy.fabfile_daemonology.sleep', lambda x: None)
    return bootstrap


def test_bootstrap(bootstrap, capsys, put_mock, run_mock, tempdir, yesno_mock):
    format_info = dict(
        bsdploy_path=bsdploy_path,
        tempdir=tempdir.directory)
    put_mock.expected = [
        (('bootstrap-files/authorized_keys', '/tmp/authorized_keys'), {}),
        (("%(bsdploy_path)s/enable_root_login_on_daemonology.sh" % format_info, '/tmp/'), {'mode': '0775'}),
        (("%(bsdploy_path)s/bootstrap-files/FreeBSD.conf" % format_info, '/usr/local/etc/pkg/repos/FreeBSD.conf'), {'mode': None}),
        (("%(bsdploy_path)s/bootstrap-files/make.conf" % format_info, '/etc/make.conf'), {'mode': None}),
        (("%(bsdploy_path)s/bootstrap-files/pkg.conf" % format_info, '/usr/local/etc/pkg.conf'), {'mode': None})]
    run_mock.expected = [
        ("su root -c '/tmp/enable_root_login_on_daemonology.sh'", {}, ''),
        ('rm /tmp/enable_root_login_on_daemonology.sh', {}, ''),
        ('mkdir -p "/usr/local/etc/pkg/repos"', {'shell': False}, ''),
        ('pkg update', {'shell': False}, ''),
        ('pkg install python27', {'shell': False}, '')]
    bootstrap()
