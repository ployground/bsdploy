# convenience Makefile to setup a development verison
# of bsdploy and its direct dependencies

develop: .installed.cfg

.installed.cfg: bin/buildout buildout.cfg bin/virtualenv
	bin/buildout -v

bin/buildout: bin/pip
	bin/pip install zc.buildout

# needed for tox
bin/virtualenv: bin/pip
	bin/pip install virtualenv

bin/pip:
	virtualenv .

clean:
	git clean -dxxf

.PHONY: clean
