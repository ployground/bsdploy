# convenience Makefile to setup a development version
# of bsdploy and its direct dependencies

develop: .installed.cfg

.installed.cfg: bin/buildout buildout.cfg bin/virtualenv
	bin/buildout -v

bin/buildout: bin/pip
	bin/pip install -U zc.buildout

# needed for tox
bin/virtualenv: bin/pip
	bin/pip install virtualenv

bin/pip:
	virtualenv -p python2.7 .

clean:
	git clean -dxxf

docs:
	make -C docs html

.PHONY: clean docs
