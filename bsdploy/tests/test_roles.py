from bsdploy import bsdploy_path
import os
import pytest


@pytest.fixture
def ctrl(ployconf, tempdir):
    from ploy import Controller
    import bsdploy
    import ploy_ezjail
    import ploy_ansible
    ployconf.fill([
        '[ez-master:jailhost]',
        'host = jailhost'])
    ctrl = Controller(configpath=ployconf.directory)
    ctrl.plugins = {
        'bsdploy': bsdploy.plugin,
        'ezjail': ploy_ezjail.plugin,
        'ansible': ploy_ansible.plugin}
    ctrl.configfile = ployconf.path
    return ctrl


def get_all_roles():
    roles_path = os.path.join(bsdploy_path, 'roles')
    roles = []
    for item in os.listdir(roles_path):
        if os.path.isdir(os.path.join(roles_path, item)):
            roles.append(item)
    return sorted(roles)


def _iter_tasks(block):
    from ansible.playbook.block import Block
    for task in block:
        if isinstance(task, Block):
            for task in _iter_tasks(task.block):
                yield task
        else:
            yield task


def iter_tasks(plays):
    for play in plays:
        for task in _iter_tasks(play.compile()):
            if task.action == 'meta':
                meta_action = task.args.get('_raw_params')
                if meta_action == 'flush_handlers':  # pragma: nocover - branch coverage only on failure
                    continue
                raise ValueError  # pragma: nocover - only on failure
            yield play, task


def test_roles(ctrl):
    instance = ctrl.instances['jailhost']
    pb = instance.get_playbook()
    plays = pb.get_plays()
    tasks = []
    for play, task in iter_tasks(plays):
        tasks.append(task.name)
    assert tasks == [
        'bind host sshd to primary ip',
        'Enable ntpd in rc.conf',
        'Disable public use of ntpd',
        'Check for old ipnat_rules setting',
        'Remove ipfilter from rc.conf',
        'Remove ipfilter_rules from rc.conf',
        'Remove ipmon from rc.conf',
        'Remove ipmon_flags from rc.conf',
        'Remove ipnat from rc.conf',
        'Remove ipnat_rules from rc.conf',
        'Enable pf in rc.conf',
        'Check for /etc/pf.conf',
        'Default pf.conf',
        'Stat of /dev/pf',
        'Checking pf',
        'Setup pf.conf',
        'Reload pf.conf',
        'Enable gateway in rc.conf',
        'Setup cloned interfaces',
        'Enable security.jail.allow_raw_sockets',
        'Enable security.jail.sysvipc_allowed',
        'Ensure helper packages are installed (using http proxy)',
        'Ensure helper packages are installed',
        'Set default jail interface',
        'Set default jail parameters',
        'Set default jail exec stop',
        'Enable jail_parallel_start',
        'Enable ezjail in rc.conf',
        'Setup ezjail.conf',
        'Setup data zpool',
        'Set data zpool options',
        'Jails ZFS file system',
        'Initialize ezjail (using http proxy)',
        'Initialize ezjail (may take a while)',
        'Create pkg cache folder',
        'Directory for jail flavour "bsdploy_base"',
        'The .ssh directory for root in bsdploy_base flavour',
        'The etc directory in bsdploy_base flavour',
        'The etc/ssh directory in bsdploy_base flavour',
        '',
        '',
        '',
        '',
        'rc.conf for bsdploy_base flavour',
        'sshd_config for bsdploy_base flavour',
        'motd for bsdploy_base flavour',
        'copy some settings from host to bsdploy_base flavour']


def test_all_role_templates_tested(ctrl, request):
    instance = ctrl.instances['jailhost']
    instance.config['roles'] = ' '.join(get_all_roles())
    pb = instance.get_playbook()
    plays = pb.get_plays()
    # import after running to avoid module import issues
    from bsdploy.tests import test_templates
    templates = []
    for play, task in iter_tasks(plays):
        if task.action != 'template':
            continue
        loader = play.get_loader()
        src = task.args.get('src')
        template_path = loader.path_dwim_relative(
            task._role._role_path, 'templates', src)
        if not os.path.exists(template_path):  # pragma: nocover - only on failure
            raise ValueError
        name = src.lower()
        for rep in ('-', '.'):
            name = name.replace(rep, '_')
        templates.append((
            name,
            dict(
                path=task._role._role_path,
                role_name=task._role.get_name(),
                name=src, task_name=task.name)))
    test_names = [x for x in dir(test_templates) if x.startswith('test_')]
    for name, info in templates:
        test_name = 'test_%s_%s' % (info['role_name'], name)
        if not any(x for x in test_names if x.startswith(test_name)):  # pragma: nocover - only on failure
            pytest.fail("No test '{0}' for template '{name}' of task '{task_name}' in role '{role_name}' at '{path}'.".format(test_name, **info))
