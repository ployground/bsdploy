# convenience Makefile to setup a development version
# of bsdploy and its direct dependencies

develop: .installed.cfg

.installed.cfg: bin/ansible bin/buildout buildout.cfg bin/virtualenv
	bin/buildout -v

# needed for tests
bin/ansible: bin/pip
	bin/pip install "ansible<2.0.0"

bin/buildout: bin/pip
	bin/pip install zc.buildout

# needed for tox
bin/virtualenv: bin/pip
	bin/pip install virtualenv

bin/pip:
	virtualenv .

clean:
	git clean -dxxf

docs:
	make -C docs html

.PHONY: clean docs
