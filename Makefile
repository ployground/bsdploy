# convenience Makefile to setup a development verison
# of bsdploy and its direct dependencies
version=2.7

develop: requirements .installed.cfg

requirements: bin/pip
	bin/pip install -r dev-requirements.txt

.installed.cfg: bin/buildout buildout.cfg
	bin/buildout -v

bin/buildout: bin/pip
	bin/pip install zc.buildout

bin/pip:
	virtualenv-$(version) .

clean:
	git clean -dxxf

.PHONY: clean requirements
