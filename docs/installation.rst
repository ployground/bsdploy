Installation
============

Since bsdploy is still in development, there are currently no packaged versions available yet.

You can however install a development version from github or alpha releases from pypi.


Installing from PyPI
--------------------

Since bsdploy and its dependencies are written in Python, you can install them from the official Python Packaging Index (a.k.a. PyPI). 

To do so, you will need Python and virtualenv installed on your system, i.e. on Mac OS X using ``homebrew`` you would install ``brew install pyenv-virtualenv``.

Since bsdploy has specific requirements in regards to Fabric and ansible (meaning, their latest version will not always work with the latest version of bsdploy until the latter is adjusted) it is strongly recommended to install bsdploy into its own virtualenv.

To use the version installed inside this virtualenv it is furthermore suggested to 'source' the python interpreter. This will add the ``bin`` directory of the virtualenv (temporarily) to your ``$PATH`` so you can use the binaries installed inside it just as if they were installed globally.

Finally, because there is no stable release of BSDploy yet, you will need to specify the exact version, otherwise ``pip`` will refuse to install it.

In summary, do this::

	virtualenv .
	source bin/activate
	pip install ansible
	pip install bsdploy==0.1a4


Installing from github
----------------------

To follow along the latest version of bsdploy you will need the same requirements as listed above plus, obviously, ``git``. Then::

	git clone https://github.com/tomster/bsdploy.git
	cd bsdploy
	make

This will check out copies of bsdploy's immediate dependencies (``mr.awsome`` and friends) and create the ploy* executables inside ``bin``. You can either add the ``bin`` directory to your path or symlink them into somewhere that's already on your path.

When keeping your checkout up-to-date it is usually a good idea to update the ``mr.awsome`` packages (located inside ``src``), as well. The best way to do so is to use the provided ``develop`` command after updating the bsdploy repository itself like so::

	git pull
	bin/develop up -v

The ``-v`` flag will show any git messages that arise during the update.

As described above, it is recommended to source the ``virtualenv`` to have a 'global' installation of BSDploy::

	source bin/activate
