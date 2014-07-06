Installation
============

Since BSDploy is still in development, there are currently no packaged versions (i.e. homebrew, pkgng, aptitude etc.) available yet.

You can however install beta releases from PyPI or a bleeding edge development version from github.


Installing from PyPI
--------------------

Since BSDploy and its dependencies are written in Python, you can install them from the official Python Packaging Index (a.k.a. PyPI). 

The short version:

.. code-block:: console
    :linenos:

	virtualenv .
	source bin/activate
	pip install ansible
	pip install --pre bsdploy

(``1``) BSDploy has specific requirements in regards to Fabric and ansible (meaning, their latest version will not neccessarily work with the latest version of BSDploy until the latter is adjusted) it is therefore strongly recommended to install BSDploy into its own virtualenv.

To do so, you will need Python and virtualenv installed on your system, i.e. on Mac OS X using ``homebrew`` you would install ``brew install pyenv-virtualenv``.

(``2``) To use the version installed inside this virtualenv it is  suggested to 'source' the python interpreter. This will add the ``bin`` directory of the virtualenv (temporarily) to your ``$PATH`` so you can use the binaries installed inside it just as if they were installed globally.

(``3``) Unfortunately, ansible's ``setup.py`` violates buildout's sandbox limitations and therefore cannot be an automatic dependency of BSDploy, so we need to install it manually for now.

(``4``) Finally, because there is no stable release of BSDploy yet, you will need to add ``--pre``, otherwise ``pip`` will refuse to install it.


Installing from github
----------------------

To follow along the latest version of BSDploy you need Python and virtualenv plus – obviously – ``git``. Then::

	git clone https://github.com/ployground/bsdploy.git
	cd bsdploy
	make

This will check out copies of BSDploy's immediate dependencies (``ploy`` and friends) and create the ploy* executables inside ``bin``. You can either add the ``bin`` directory to your path or symlink them into somewhere that's already on your path, but as described above, it is recommended to source the ``virtualenv`` to have a 'global' installation of BSDploy::

	source bin/activate

When keeping your checkout up-to-date it is usually a good idea to update the ``ploy`` packages (located inside ``src``), as well. The best way to do so is to use the provided ``develop`` command after updating the bsdploy repository itself like so::

	git pull
	bin/develop up -v

The ``-v`` flag will show any git messages that arise during the update.
