import pytest


@pytest.fixture
def ctrl(ployconf, tempdir):
    from ploy import Controller
    import bsdploy
    import ploy_ezjail
    import ploy_ansible
    ployconf.fill([
        '[ez-master:jailhost]'])
    ctrl = Controller(configpath=ployconf.directory)
    ctrl.plugins = {
        'bsdploy': bsdploy.plugin,
        'ezjail': ploy_ezjail.plugin,
        'ansible': ploy_ansible.plugin}
    ctrl.configfile = ployconf.path
    return ctrl


def test_roles(ctrl, monkeypatch):
    instance = ctrl.instances['jailhost']
    pb = instance.get_playbook()
    plays = []
    monkeypatch.setattr('ansible.playbook.PlayBook._run_play', plays.append)
    pb.run()
    tasks = []
    for play in plays:
        for task in play.tasks():
            if task.meta:
                if task.meta == 'flush_handlers':
                    continue
                raise ValueError
            tasks.append(task.name)
    assert tasks == [
        'bind host sshd to primary ip',
        'Enable ntpd in rc.conf',
        'Disable public use of ntpd',
        'Enable ipfilter in rc.conf',
        'Set ipfilter_rules in rc.conf',
        'Setup ipf.rules',
        'Enable ipmon in rc.conf',
        'Set ipmon_flags in rc.conf',
        'Enable ipnat in rc.conf',
        'Set ipnat_rules in rc.conf',
        'Setup ipnat.rules',
        'Enable gateway in rc.conf',
        'Add lo1 to rc.conf',
        'Enable allow_raw_sockets',
        'Enable sysvipc_allowed',
        'Ensure helper packages are installed',
        'Set default jail interface',
        'Set default jail parameters',
        'Set default jail exec stop',
        'Enable ezjail in rc.conf',
        'Setup ezjail.conf',
        'Setup data zpool',
        'Setup rc.conf lines for data zpool',
        'Set data zpool options',
        'Jails ZFS file system',
        'Initialize ezjail (may take a while)',
        'Download pkg.txz',
        'Directory for jail flavour "base"',
        'Pkg in base flavour',
        'The .ssh directory for root in base flavour',
        'The etc directory in base flavour',
        'The etc/ssh directory in base flavour',
        'copy src=make.conf dest=/usr/jails/flavours/base/etc/make.conf owner=root group=wheel',
        'file dest=/usr/jails/flavours/base/usr/local/etc/pkg/repos state=directory owner=root group=wheel',
        'copy src=pkg.conf dest=/usr/jails/flavours/base/usr/local/etc/pkg.conf owner=root group=wheel',
        'template src=FreeBSD.conf dest=/usr/jails/flavours/base/usr/local/etc/pkg/repos/FreeBSD.conf owner=root group=wheel',
        'rc.conf for base flavour',
        'sshd_config for base flavour',
        'motd for base flavour',
        'copy some settings from host to base flavour']
