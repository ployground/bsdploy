import pytest
from mock import Mock
from bsdploy import bootstrap_utils as bu


@pytest.fixture
def run_mock(monkeypatch):
    run = Mock()

    def _run(command, **kwargs):
        try:
            expected = run.expected.pop(0)
        except IndexError:
            expected = '', '', ''
        cmd, kw, result = expected
        assert command == cmd
        assert kwargs == kw
        return result

    run.side_effect = _run
    run.expected = []
    monkeypatch.setattr(bu, 'run', run)
    return run


@pytest.fixture
def env_mock(monkeypatch):
    from fabric.utils import _AttributeDict
    env = _AttributeDict()
    monkeypatch.setattr(bu, 'env', env)
    return env


def test_get_realmem(run_mock):
    run_mock.expected = [('sysctl -n hw.realmem', {}, '536805376')]
    assert bu.get_realmem() == 512


def test_get_interfaces(run_mock):
    run_mock.expected = [('ifconfig -l', {}, 'em0 em1 lo0 lo1')]
    assert bu.get_interfaces() == ['em0', 'em1', 'lo0', 'lo1']


default_mounts = '\n'.join([
    '/dev/md0 on / (ufs, local, read-only)',
    'devfs on /dev (devfs, local, multilabel)',
    'tmpfs on /rw (tmpfs, local)',
    'devfs on /rw/dev (devfs, local, multilabel)'])


def test_get_devices(run_mock, env_mock):
    run_mock.expected = [
        ('mount', {}, default_mounts),
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    env_mock.instance = Mock()
    env_mock.instance.config = {}
    assert bu.get_devices() == set(['ada0'])


def test_get_devices_cdrom_mounted(run_mock, env_mock):
    run_mock.expected = [
        ('mount', {}, '\n'.join([
            default_mounts,
            '/dev/cd0 on /rw/cdrom (cd9660, local, read-only)'])),
        ('sysctl -n kern.disks', {}, 'ada0 cd0\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    env_mock.instance = Mock()
    env_mock.instance.config = {}
    assert bu.get_devices() == set(['ada0'])


def test_get_devices_usb_mounted(run_mock, env_mock):
    run_mock.expected = [
        ('mount', {}, '\n'.join([
            default_mounts,
            '/dev/da0a on /rw/media (ufs, local, read-only)'])),
        ('sysctl -n kern.disks', {}, 'ada0 da0\n'),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n')]
    env_mock.instance = Mock()
    env_mock.instance.config = {}
    assert bu.get_devices() == set(['ada0'])


def test_get_devices_different_cdrom(run_mock, env_mock):
    run_mock.expected = [
        ('mount', {}, default_mounts),
        ('sysctl -n kern.disks', {}, 'ada0 cd1\n'),
        ('test -e /dev/cd1 && mount_cd9660 /dev/cd1 /cdrom || true', {}, '\n'),
        ('test -e /dev/da0a && mount -o ro /dev/da0a /media || true', {}, '\n')]
    env_mock.instance = Mock()
    env_mock.instance.config = {'bootstrap-cd-device': 'cd1'}
    assert bu.get_devices() == set(['ada0'])


def test_get_devices_different_usb(run_mock, env_mock):
    run_mock.expected = [
        ('mount', {}, default_mounts),
        ('sysctl -n kern.disks', {}, 'ada0 cd0 da1\n'),
        ('test -e /dev/cd0 && mount_cd9660 /dev/cd0 /cdrom || true', {}, '\n'),
        ('test -e /dev/da1a && mount -o ro /dev/da1a /media || true', {}, '\n')]
    env_mock.instance = Mock()
    env_mock.instance.config = {'bootstrap-usb-device': 'da1a'}
    assert bu.get_devices() == set(['ada0'])
