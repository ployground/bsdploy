import os
import pytest
import re
import subprocess
import textwrap
import time


@pytest.fixture
def qs_path():
    from bsdploy import bsdploy_path
    qs_path = os.path.abspath(os.path.join(bsdploy_path, '..', 'docs', 'quickstart.rst'))
    if not os.path.exists(qs_path):
        pytest.skip("Can't access quickstart.rst")
    return qs_path


def strip_block(block):
    lines = iter(block)
    result = []
    for line in lines:
        if not line:
            continue
        result.append(line)
        break
    result.extend(lines)
    lines = iter(reversed(result))
    result = []
    for line in lines:
        if not line:
            continue
        result.append(line)
        break
    result.extend(lines)
    return textwrap.dedent("\n".join(reversed(result))).split('\n')


def iter_blocks(lines):
    inindent = False
    text = []
    block = []
    for line in lines:
        line = line.rstrip()
        if inindent and line and line.strip() == line:
            inindent = False
            text = '\n'.join(text)
            text = re.sub('([^\n])\n([^\n])', '\\1\\2', text)
            text = re.split('\\n+', text)
            yield text, strip_block(block)
            text = []
            block = []
        if inindent:
            block.append(line)
        else:
            text.append(line)
        if line.endswith('::') or line.startswith('.. code-block::'):
            inindent = True


def parse_qs(qs_path):
    with open(qs_path) as f:
        lines = f.read().splitlines()
    result = []
    for text, block in iter_blocks(lines):
        text = '\n'.join(text)
        if block[0].startswith('%'):
            result.append(('execute', block))
        elif '``' in text:
            names = re.findall('``(.+?)``', text)
            if 'create' in text.lower():
                result.append(('create', names, block))
            if 'add' in text.lower():
                result.append(('add', names, block))
        elif 'completed' in text:
            result.append(('expect', block))
    return result


def iter_quickstart_calls(actions, tempdir):
    paths = {
        'ploy.conf': tempdir['etc/ploy.conf'],
        'etc/ploy.conf': tempdir['etc/ploy.conf'],
        'jailhost.yml': tempdir['host_vars/jailhost.yml'],
        'jailhost-demo_jail.yml': tempdir['jailhost-demo_jail.yml']}
    for action in actions:
        if action[0] == 'execute':
            for line in action[1]:
                if line.startswith('%'):
                    line = line[1:].strip()
                    parts = line.split()
                    if len(parts) == 3 and parts[:2] == ['ploy', 'ssh']:
                        continue
                    bootstrap = line.endswith('bootstrap')
                    if bootstrap:
                        yield (action[0], time.sleep, (120,), {})
                        line = '%s -y' % line
                    yield (action[0], subprocess.check_call, (line,), dict(shell=True))
                    if bootstrap:
                        yield (action[0], time.sleep, (120,), {})
        elif action[0] == 'create':
            name = action[1][-1]
            content = list(action[2])
            content.append('')
            yield (action[0], paths[name].fill, (content,), {})
        elif action[0] == 'add':
            name = action[1][-1]
            with open(paths[name].path) as f:
                content = f.read().split('\n')
            content.extend(action[2])
            content.append('')
            yield (action[0], paths[name].fill, (content,), {})
        elif action[0] == 'expect':
            pass
        else:
            pytest.fail("Unknown action %s" % action[0])


def test_quickstart_calls(qs_path, tempdir):
    from pprint import pprint
    calls = []
    for action, func, args, kw in iter_quickstart_calls(parse_qs(qs_path), tempdir):
        if action in ('add', 'create'):
            func(*args, **kw)
            calls.append((action, func.__self__.path))
        else:
            calls.append((func, args))
    pprint(calls)
    assert calls == [
        (subprocess.check_call, ('pip install --pre ploy_virtualbox',)),
        (subprocess.check_call, ('mkdir ploy-quickstart',)),
        (subprocess.check_call, ('cd ploy-quickstart',)),
        (subprocess.check_call, ('mkdir downloads',)),
        (subprocess.check_call, ('ploy-download file:///Users/fschulze/downloads/archives/mfsbsd-se-9.2-RELEASE-amd64.iso 4ef70dfd7b5255e36f2f7e1a5292c7a05019c8ce downloads/',)),
        (subprocess.check_call, ('mkdir etc',)),
        ('create', '%s/etc/ploy.conf' % tempdir.directory),
        (subprocess.check_call, ('ploy start ploy-demo',)),
        ('add', '%s/etc/ploy.conf' % tempdir.directory),
        (time.sleep, (120,)),
        (subprocess.check_call, ('ploy bootstrap -y',)),
        (time.sleep, (120,)),
        ('add', '%s/etc/ploy.conf' % tempdir.directory),
        (subprocess.check_call, ('ploy configure jailhost',)),
        ('add', '%s/etc/ploy.conf' % tempdir.directory),
        (subprocess.check_call, ('ploy start demo_jail',)),
        ('create', '%s/jailhost-demo_jail.yml' % tempdir.directory),
        (subprocess.check_call, ('ploy configure demo_jail',)),
        (subprocess.check_call, ('mkdir host_vars',)),
        ('create', '%s/host_vars/jailhost.yml' % tempdir.directory),
        (subprocess.check_call, ('ploy configure jailhost -t ipnat_rules',)),
        (subprocess.check_call, ("ploy ssh jailhost 'ifconfig em0'",))]


@pytest.yield_fixture
def virtualenv(tempdir):
    origdir = os.getcwd()
    os.chdir(tempdir.directory)
    subprocess.check_output(['virtualenv', '.'])
    orig_env = dict(os.environ)
    os.environ.pop('PYTHONHOME', None)
    os.environ['VIRTUAL_ENV'] = tempdir.directory
    os.environ['PATH'] = '%s/bin:%s' % (tempdir.directory, orig_env['PATH'])
    yield tempdir.directory
    if 'PYTHONHOME' in orig_env:
        os.environ['PYTHONHOME'] = orig_env['PYTHONHOME']
    os.environ.pop('PATH', None)
    if 'PATH' in orig_env:
        os.environ['PATH'] = orig_env['PATH']
    os.environ.pop('VIRTUAL_ENV', None)
    if 'VIRTUAL_ENV' in orig_env:
        os.environ['VIRTUAL_ENV'] = orig_env['VIRTUAL_ENV']
    os.chdir(origdir)


@pytest.mark.skipif("not config.option.quickstart_bsdploy")
def test_quickstart(request, qs_path, tempdir, virtualenv):
    if not os.path.isabs(request.config.option.quickstart_bsdploy):
        pytest.fail("The path given by --quickstart-bsdploy needs to be absolute.")
    subprocess.check_call(['pip', 'install', '--pre', request.config.option.quickstart_bsdploy])
    for action, func, args, kw in iter_quickstart_calls(parse_qs(qs_path), tempdir):
        func(*args, **kw)
