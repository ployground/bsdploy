from mock import Mock
import pytest


@pytest.fixture(autouse=True)
def cleanup_modules(request):
    import inspect
    import sys
    for modname, module in list(sys.modules.items()):
        if module is None:
            continue
        for name, member in inspect.getmembers(module):
            if not hasattr(member, '__class__'):
                continue
            if member.__class__.__module__.startswith('fabric'):
                del sys.modules[modname]
                break


@pytest.fixture
def ctrl(ployconf):
    from ploy import Controller
    import bsdploy
    import ploy_ezjail
    import ploy_fabric
    ployconf.fill([
        '[ez-master:jailhost]'
        '[instance:foo]',
        'master = jailhost'])
    ctrl = Controller(configpath=ployconf.directory)
    ctrl.plugins = {
        'bsdploy': bsdploy.plugin,
        'ezjail': ploy_ezjail.plugin,
        'fabric': ploy_fabric.plugin}
    return ctrl


def test_bootstrap_command(ctrl, monkeypatch):
    bootstrap = Mock()
    monkeypatch.setattr('bsdploy.fabrics.bootstrap_mfsbsd', bootstrap)
    ctrl(['./bin/ploy', 'bootstrap'])
    assert bootstrap.called
