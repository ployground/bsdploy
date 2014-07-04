from mock import Mock
import pytest


default_mounts = '\n'.join([
    '/dev/md0 on / (ufs, local, read-only)',
    'devfs on /dev (devfs, local, multilabel)',
    'tmpfs on /rw (tmpfs, local)',
    'devfs on /rw/dev (devfs, local, multilabel)'])


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
    monkeypatch.setattr('bsdploy.fabrics.run', run)
    return run


@pytest.fixture
def env_mock(fabric_integration, monkeypatch):
    from fabric.utils import _AttributeDict
    env = _AttributeDict()
    env.instance = Mock()
    env.instance.config = {}
    monkeypatch.setattr('bsdploy.bootstrap_utils.env', env)
    monkeypatch.setattr('bsdploy.fabrics.env', env)
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
    monkeypatch.setattr('bsdploy.fabrics.yesno', yesno)
    monkeypatch.setattr('ploy.common.yesno', yesno)
    return yesno
