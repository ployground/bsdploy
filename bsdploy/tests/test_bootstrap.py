import pytest
from mock import patch, MagicMock
from bsdploy import bootstrap_utils as bu


def test_get_realmem():
    with patch('bsdploy.bootstrap_utils.run') as mocked_run:
        mocked_run.return_value = '536805376'
        assert bu.get_realmem() == 512


def test_get_interfaces():
    with patch('bsdploy.bootstrap_utils.run') as mocked_run:
        mocked_run.return_value = 'em0 em1 lo0 lo1'
        assert bu.get_interfaces() == ['em0', 'em1', 'lo0', 'lo1']


@pytest.yield_fixture
def run_mock(monkeypatch, request):

    return_values = request.keywords['run_return_values'].args[0]

    def popper(*args, **kwargs):
        try:
            return return_values.pop(0)
        except IndexError:
            pytest.fail('Called `run` more than expected')

    mocked_run = MagicMock(side_effect=popper)
    monkeypatch.setattr('bsdploy.bootstrap_utils.run', mocked_run)
    yield mocked_run


@pytest.yield_fixture
def env_mock(monkeypatch, request):
    env = MagicMock()
    monkeypatch.setattr('bsdploy.bootstrap_utils.env', env)
    yield env


@pytest.mark.run_return_values([
    '''system/root on / (zfs, local, nfsv4acls)\r\ndevfs on /dev (devfs, local, multilabel)\r\nsystem/root/tmp on /tmp (zfs, local, nfsv4acls)\r\nsystem/root/var on /var (zfs, local, nfsv4acls)\r\ntank/jails on /usr/jails (zfs, local, noatime, nfsv4acls)\r\ntank/jails/basejail on /usr/jails/basejail (zfs, local, noatime, nfsv4acls)\r\ntank/jails/newjail on /usr/jails/newjail (zfs, local, noatime, nfsv4acls)\r\ntank/jails/demo_jail on /usr/jails/demo_jail (zfs, local, noatime, nfsv4acls)\r\n/usr/jails/basejail on /usr/jails/demo_jail/basejail (nullfs, local, read-only)\r\ndevfs on /usr/jails/demo_jail/dev (devfs, local, multilabel)\r\nfdescfs on /usr/jails/demo_jail/dev/fd (fdescfs)
    ''',
    'cd0 ada0',
    'mount_cd9660: /cdrom: No such file or directory',
    '',
])
def test_get_devices(run_mock, env_mock):
    env_mock.server = MagicMock()
    env_mock.server.config = {'bootstrap-cd-device': 'cd0'}
    assert bu.get_devices() == set(['ada0'])
