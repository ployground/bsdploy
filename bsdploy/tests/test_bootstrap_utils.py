import pytest
from mock import Mock
from bsdploy import bootstrap_utils as bu


@pytest.fixture
def run_mock(monkeypatch):
    run = Mock()
    monkeypatch.setattr(bu, 'run', run)
    return run


@pytest.fixture
def env_mock(monkeypatch):
    from fabric.utils import _AttributeDict
    env = _AttributeDict()
    monkeypatch.setattr(bu, 'env', env)
    return env


def test_get_realmem(run_mock):
    run_mock.return_value = '536805376'
    assert bu.get_realmem() == 512


def test_get_interfaces(run_mock):
    run_mock.return_value = 'em0 em1 lo0 lo1'
    assert bu.get_interfaces() == ['em0', 'em1', 'lo0', 'lo1']


def test_get_devices(run_mock, env_mock):
    run_mock.side_effect = [
        '''system/root on / (zfs, local, nfsv4acls)\r\ndevfs on /dev (devfs, local, multilabel)\r\nsystem/root/tmp on /tmp (zfs, local, nfsv4acls)\r\nsystem/root/var on /var (zfs, local, nfsv4acls)\r\ntank/jails on /usr/jails (zfs, local, noatime, nfsv4acls)\r\ntank/jails/basejail on /usr/jails/basejail (zfs, local, noatime, nfsv4acls)\r\ntank/jails/newjail on /usr/jails/newjail (zfs, local, noatime, nfsv4acls)\r\ntank/jails/demo_jail on /usr/jails/demo_jail (zfs, local, noatime, nfsv4acls)\r\n/usr/jails/basejail on /usr/jails/demo_jail/basejail (nullfs, local, read-only)\r\ndevfs on /usr/jails/demo_jail/dev (devfs, local, multilabel)\r\nfdescfs on /usr/jails/demo_jail/dev/fd (fdescfs)\n''',
        'cd0 ada0\n',
        'mount_cd9660: /cdrom: No such file or directory\n',
        '']
    env_mock.instance = Mock()
    env_mock.instance.config = {'bootstrap-cd-device': 'cd0'}
    assert bu.get_devices() == set(['ada0'])
