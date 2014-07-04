from bsdploy import bootstrap_utils
from bsdploy.tests.conftest import default_mounts, run_result
import pytest


@pytest.fixture
def bu(env_mock, run_mock):
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
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('/cdrom/9.2-RELEASE-amd64', 0))]
    assert bu.bsd_url == '/cdrom/9.2-RELEASE-amd64'


def test_bsd_url_not_found(bu, run_mock):
    run_mock.expected = [
        ("find /cdrom/ /media/ -name 'base.txz' -exec dirname {} \\;", {}, run_result('', 1))]
    assert bu.bsd_url is None


def test_bsd_url_from_config(bu, run_mock, env_mock):
    env_mock.instance.config = {'bootstrap-bsd-url': '/foo'}
    assert bu.bsd_url == '/foo'
