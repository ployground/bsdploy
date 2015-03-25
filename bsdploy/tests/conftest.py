from mock import Mock
from ploy.tests.conftest import ployconf, tempdir
import pytest


(ployconf, tempdir)  # shutup pyflakes


def pytest_addoption(parser):
    parser.addoption(
        "--quickstart-bsdploy", help="Run the quickstart with this bsdploy sdist",
        action="store", dest="quickstart_bsdploy")
    parser.addoption(
        "--ansible-version", help="The ansible version to use for quickstart tests, defaults to newest",
        action="store", dest="ansible_version")


default_mounts = '\n'.join([
    '/dev/md0 on / (ufs, local, read-only)',
    'devfs on /dev (devfs, local, multilabel)',
    'tmpfs on /rw (tmpfs, local)',
    'devfs on /rw/dev (devfs, local, multilabel)'])


@pytest.fixture
def ctrl(ployconf, tempdir):
    from ploy import Controller
    import ploy.tests.dummy_plugin
    ctrl = Controller(tempdir.directory)
    ctrl.plugins = {
        'dummy': ploy.tests.dummy_plugin.plugin}
    ctrl.configfile = ployconf.path
    return ctrl


@pytest.fixture
def fabric_integration():
    from ploy_fabric import _fabric_integration
    # this needs to be done before any other fabric module import
    _fabric_integration.patch()


class RunResult(str):
    pass


def run_result(out, rc):
    result = RunResult(out)
    result.return_code = rc
    result.succeeded = rc == 0
    result.failed = rc != 0
    return result


@pytest.fixture
def run_mock(fabric_integration, monkeypatch):
    run = Mock()

    def _run(command, **kwargs):
        try:
            expected = run.expected.pop(0)
        except IndexError:  # pragma: nocover
            expected = '', '', ''
        cmd, kw, result = expected
        assert command == cmd
        assert kwargs == kw
        return result

    run.side_effect = _run
    run.expected = []
    monkeypatch.setattr('bsdploy.bootstrap_utils.run', run)
    monkeypatch.setattr('fabric.contrib.files.run', run)
    return run


@pytest.fixture
def put_mock(fabric_integration, monkeypatch):
    put = Mock()

    def _put(*args, **kw):
        try:
            expected = put.expected.pop(0)
        except IndexError:  # pragma: nocover
            expected = ((), {})
        eargs, ekw = expected
        assert len(args) == len(eargs)
        for arg, earg in zip(args, eargs):
            if earg is object:
                continue
            if hasattr(arg, 'name'):
                assert arg.name == earg
            else:
                assert arg == earg
        assert sorted(kw.keys()) == sorted(ekw.keys())
        for k in kw:
            if ekw[k] is object:
                continue
            assert kw[k] == ekw[k], "kw['%s'](%r) != ekw['%s'](%r)" % (k, kw[k], k, ekw[k])

    put.side_effect = _put
    put.expected = []
    monkeypatch.setattr('bsdploy.bootstrap_utils.put', put)
    monkeypatch.setattr('fabric.contrib.files.put', put)
    return put


@pytest.fixture
def local_mock(fabric_integration, monkeypatch):
    from mock import Mock
    local = Mock()

    def _local(command, **kwargs):
        try:
            expected = local.expected.pop(0)
        except IndexError:  # pragma: nocover
            expected = '', '', ''
        cmd, kw, result = expected
        assert command == cmd
        assert kwargs == kw
        return result

    local.side_effect = _local
    local.expected = []
    monkeypatch.setattr('bsdploy.bootstrap_utils.local', local)
    return local


@pytest.fixture
def env_mock(ctrl, fabric_integration, monkeypatch, ployconf):
    from fabric.api import env
    ployconf.fill([
        '[dummy-instance:test_instance]'])
    env.instance = ctrl.instances['test_instance']
    return env


@pytest.fixture
def environ_mock(monkeypatch):
    environ = {}
    monkeypatch.setattr('os.environ', environ)
    return environ


@pytest.fixture
def yesno_mock(monkeypatch):
    yesno = Mock()

    def _yesno(question):
        try:
            expected = yesno.expected.pop(0)
        except IndexError:  # pragma: nocover
            expected = '', False
        cmd, result = expected
        assert question == cmd
        print question
        return result

    yesno.side_effect = _yesno
    yesno.expected = []
    monkeypatch.setattr('bsdploy.bootstrap_utils.yesno', yesno)
    monkeypatch.setattr('ploy.common.yesno', yesno)
    return yesno
