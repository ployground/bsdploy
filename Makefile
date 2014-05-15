# convenience Makefile to setup a development verison
# of bsdploy and its direct dependencies

develop: bin/pip .installed.cfg
	bin/pip install -r dev-requirements.txt

bin/pip:
	virtualenv-$(version) .

bin/buildout: bin/pip
	bin/pip install zc.buildout

.installed.cfg: bin/buildout buildout.cfg
	bin/buildout -v
