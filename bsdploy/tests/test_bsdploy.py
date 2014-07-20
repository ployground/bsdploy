import os
import pytest


@pytest.fixture
def ctrl(ployconf, tempdir):
    from ploy import Controller
    import bsdploy
    import ploy.plain
    import ploy_ezjail
    import ploy_fabric
    ployconf.fill([
        '[ez-master:jailhost]',
        '[instance:foo]',
        'master = jailhost'])
    ctrl = Controller(configpath=ployconf.directory)
    ctrl.plugins = {
        'bsdploy': bsdploy.plugin,
        'ezjail': ploy_ezjail.plugin,
        'fabric': ploy_fabric.plugin,
        'plain': ploy.plain.plugin}
    ctrl.configfile = ployconf.path
    return ctrl


def test_bootstrap_command(capsys, ctrl, monkeypatch):
    def do(self, *args, **kwargs):
        print "do with %r, %r called!" % (args, kwargs)
    monkeypatch.setattr('ploy_fabric.do', do)
    ctrl(['./bin/ploy', 'bootstrap'])
    (out, err) = capsys.readouterr()
    out_lines = out.splitlines()
    assert out_lines == [
        "do with ('bootstrap',), {'bootstrap-yes': False} called!"]


def test_augment_ezjail_master(ctrl, ployconf, tempdir):
    tempdir['bootstrap-files/ssh_host_rsa_key.pub'].fill('rsa')
    config = dict(ctrl.instances['jailhost'].config)
    assert sorted(config.keys()) == [
        'ansible_python_interpreter', 'fabfile', 'fabric-shell', 'fingerprint',
        'roles']
    assert config['ansible_python_interpreter'] == '/usr/local/bin/python2.7'
    assert config['fabfile'].endswith('fabfile_mfsbsd.py')
    assert config['fabric-shell'] == '/bin/sh -c'
    assert config['fingerprint'].endswith('bootstrap-files/ssh_host_rsa_key.pub')
    assert os.path.exists(config['fabfile']), "The fabfile '%s' doesn't exist." % config['fabfile']
    assert config['roles'] == 'jails_host'


def test_augment_ezjail_master_playbook_implicit(ctrl, ployconf, tempdir):
    from ploy_ansible import has_playbook
    jailhost_yml = tempdir['jailhost.yml']
    jailhost_yml.fill('')
    config = dict(ctrl.instances['jailhost'].config)
    assert 'roles' not in config
    assert 'playbook' not in config
    assert has_playbook(ctrl.instances['jailhost'])


def test_augment_ezjail_master_playbook_explicit(ctrl, ployconf, tempdir):
    from ploy_ansible import has_playbook
    ployconf.fill([
        '[ez-master:jailhost]',
        'playbook = blubber.yml'])
    config = dict(ctrl.instances['jailhost'].config)
    assert 'roles' not in config
    assert config['playbook'] == 'blubber.yml'
    assert has_playbook(ctrl.instances['jailhost'])


def test_augment_ezjail_instance(ctrl, ployconf):
    config = dict(ctrl.instances['foo'].config)
    assert sorted(config.keys()) == [
        'ansible_python_interpreter', 'fabric-shell', 'flavour', 'master',
        'startup_script']
    assert config['ansible_python_interpreter'] == '/usr/local/bin/python2.7'
    assert config['fabric-shell'] == '/bin/sh -c'
    assert config['flavour'] == 'bsdploy_base'
    assert config['master'] == 'jailhost'
    assert config['startup_script']['path'].endswith('startup-ansible-jail.sh')
    assert os.path.exists(config['startup_script']['path']), "The startup_script at '%s' doesn't exist." % config['startup_script']['path']


def test_augment_non_ezjail_instance(ctrl, ployconf):
    ployconf.fill([
        '[plain-instance:foo]'])
    assert dict(ctrl.instances['foo'].config) == {}


@pytest.mark.parametrize("instance, key, value, expected", [
    ('foo', 'ansible_python_interpreter', 'python2.7', 'python2.7'),
    ('foo', 'startup_script', 'foo', {'path': '{tempdir}/etc/foo'}),
    ('foo', 'flavour', 'foo', 'foo'),
    ('jailhost', 'bootstrap', 'daemonology', ('fabfile', '{bsdploy_path}/fabfile_daemonology.py')),
    ('jailhost', 'bootstrap', 'foo', SystemExit),
    ('jailhost', 'fabfile', 'fabfile.py', '{tempdir}/etc/fabfile.py'),
    ('jailhost', 'fabfile', 'fab1file.py', SystemExit)])
def test_augment_overwrite(ctrl, instance, key, value, expected, ployconf, tempdir):
    from bsdploy import bsdploy_path
    ployconf.fill([
        '[ez-master:jailhost]',
        '%s = %s' % (key, value),
        '[instance:foo]',
        'master = jailhost',
        '%s = %s' % (key, value)])
    tempdir['etc/fabfile.py'].fill('')
    try:
        config = dict(ctrl.instances[instance].config)
    except BaseException as e:
        assert type(e) == expected
    else:
        format_info = dict(
            bsdploy_path=bsdploy_path,
            tempdir=tempdir.directory)
        if isinstance(expected, tuple):
            key, expected = expected
        if isinstance(expected, dict):
            for k, v in expected.items():
                expected[k] = v.format(**format_info)
        else:
            expected = expected.format(**format_info)
        assert config[key] == expected
