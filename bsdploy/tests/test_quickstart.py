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
                        yield (action[0], time.sleep, (90,), {})
                        line = '%s -y' % line
                    yield (action[0], subprocess.check_call, (line,), dict(shell=True))
                    if bootstrap:
                        yield (action[0], time.sleep, (90,), {})
        elif action[0] == 'create':
            name = action[1][-1]
            content = list(action[2])
            content.append('')
            yield (action[0], paths[name].fill, (content,), {})
        elif action[0] == 'add':
            name = action[1][-1]
            content = paths[name].content().split('\n')
            content.extend(action[2])
            content.append('')
            yield (action[0], paths[name].fill, (content,), {})
        elif action[0] == 'expect':
            pass
        else:
            pytest.fail("Unknown action %s" % action[0])


def test_quickstart_calls(qs_path, tempdir):
    calls = []
    for action, func, args, kw in iter_quickstart_calls(parse_qs(qs_path), tempdir):
        if action in ('add', 'create'):
            func(*args, **kw)
            calls.append((action, func.__self__.path))
        else:
            calls.append((func, args))
    assert calls == [
        (subprocess.check_call, ('pip install --pre ploy_virtualbox',)),
        (subprocess.check_call, ('mkdir ploy-quickstart',)),
        (subprocess.check_call, ('cd ploy-quickstart',)),
        (subprocess.check_call, ('mkdir downloads',)),
        (subprocess.check_call, ('ploy-download http://mfsbsd.vx.sk/files/iso/10/amd64/mfsbsd-se-10.0-RELEASE-amd64.iso 06165ce1e06ff8e4819e86c9e23e7d149f820bb4 downloads/',)),
        (subprocess.check_call, ('mkdir etc',)),
        ('create', '%s/etc/ploy.conf' % tempdir.directory),
        (subprocess.check_call, ('ploy start ploy-demo',)),
        ('add', '%s/etc/ploy.conf' % tempdir.directory),
        (time.sleep, (90,)),
        (subprocess.check_call, ('ploy bootstrap -y',)),
        (time.sleep, (90,)),
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
    assert tempdir['etc/ploy.conf'].content().splitlines() == [
        '[vb-hostonlyif:vboxnet0]',
        'ip = 192.168.56.1',
        '',
        '[vb-dhcpserver:vboxnet0]',
        'ip = 192.168.56.2',
        'netmask = 255.255.255.0',
        'lowerip = 192.168.56.100',
        'upperip = 192.168.56.254',
        '',
        '[vb-instance:ploy-demo]',
        'vm-ostype = FreeBSD_64',
        'vm-memory = 512',
        'vm-accelerate3d = off',
        'vm-acpi = on',
        'vm-rtcuseutc = on',
        'vm-boot1 = disk',
        'vm-boot2 = dvd',
        'vm-nic1 = hostonly',
        'vm-hostonlyadapter1 = vboxnet0',
        'vm-nic2 = nat',
        'vm-natpf2 = ssh,tcp,,44003,,22',
        'storage =',
        '    --type dvddrive --medium ../downloads/mfsbsd-se-10.0-RELEASE-amd64.iso',
        '    --medium vb-disk:boot',
        '',
        '[vb-disk:boot]',
        'size = 102400',
        '',
        '[ez-master:jailhost]',
        'instance = ploy-demo',
        '',
        '[ez-master:jailhost]',
        'instance = ploy-demo',
        'roles =',
        '    dhcp_host',
        '    jails_host',
        '',
        '[ez-instance:demo_jail]',
        'ip = 10.0.0.1']
    assert tempdir['jailhost-demo_jail.yml'].content().splitlines() == [
        '---',
        '- hosts: jailhost-demo_jail',
        '  tasks:',
        '    - name: install nginx',
        '      pkgng: name=nginx state=present',
        '    - name: enable nginx at startup time',
        '      lineinfile:',
        '        dest: /etc/rc.conf',
        '        regexp: ^nginx_enable=',
        '        line: nginx_enable=\\"YES\\"',
        '    - name: make sure nginx is running or reloaded',
        '      service: name=nginx state=restarted']
    assert tempdir['host_vars/jailhost.yml'].content().splitlines() == [
        'ipnat_rules:',
        '    - "rdr em0 {{ ansible_em0.ipv4[0].address }}/32 port 80 -> {{ hostvars[\'jailhost-demo_jail\'][\'ploy_ip\'] }} port 80"']


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
    if request.config.option.ansible_version:
        subprocess.check_call(['pip', 'install', 'ansible==%s' % request.config.option.ansible_version])
    subprocess.check_call(['pip', 'install', '--pre', request.config.option.quickstart_bsdploy])
    for action, func, args, kw in iter_quickstart_calls(parse_qs(qs_path), tempdir):
        func(*args, **kw)
