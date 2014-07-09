Client requirements
===================

BSDploy and its dependencies are written in `Python <http://python.org>`_ and thus should run on pretty much any platform, although it's currently only been tested on Mac OS X and FreeBSD.


Server requirements
===================

A FreeBSD system that wants to be managed by BSDploy will need to have `ezjail <http://erdgeist.org/arts/software/ezjail/>`_ installed, as well as `Python <http://python.org>`_ and must have SSH access enabled (either for root or with ``sudo`` configured).

Strictly speaking, BSDploy only needs Python for the initial configuration of the jailhost. If you chose to perform that step yourself or use a pre-existing host, you won't need Python on the host, just ezjail.

BSDPloy can take care of these requirements for you during bootstrapping but of course you can also use it to manage existing machines that already meet them.

BSDploy currently only supports FreeBSD 9.2 (although in theory any 9.x should work) but not yet FreeBSD 10. But that is only a matter of time. We can't wait to use it on 10 ourselves :-)


Client Installation
===================

Since BSDploy is still early in development, there is currently only a packaged version for FreeBSD but no others such as i.e. homebrew, aptitude etc.) available yet.

You can however install beta releases from PyPI or a bleeding edge development version from github.


Installing on FreeBSD
---------------------

BSDploy is available from FreeBSD ports as ``sysutils/bsdploy``, for details `check it at FreshPorts <http://www.freshports.org/sysutils/bsdploy/>`_.


Installing from PyPI
--------------------

BSDploy and its dependencies are written in Python, so you can install them from the official Python Packaging Index (a.k.a. PyPI). 

The short version:

.. code-block:: console
    :linenos:

    virtualenv .
    source bin/activate
    pip install --pre bsdploy

(``1``) BSDploy has specific requirements in regards to Fabric and ansible (meaning, their latest version will not neccessarily work with the latest version of BSDploy until the latter is adjusted) it is therefore strongly recommended to install BSDploy into its own virtualenv.

To do so, you will need Python and virtualenv installed on your system, i.e. 

- on **Mac OS X** using ``homebrew`` you would install ``brew install pyenv-virtualenv``.
- on **FreeBSD** using ``pgk`` you would ``pkg install py27-virtualenv``

(``2``) To use the version installed inside this virtualenv it is  suggested to 'source' the python interpreter. This will add the ``bin`` directory of the virtualenv (temporarily) to your ``$PATH`` so you can use the binaries installed inside it just as if they were installed globally. Note, that the default ``activate`` works for bash, if you're using ``tcsh`` (the default on FreeBSD you will have to ``source bin/activate.csh``)

(``3``) Because there is no stable release of BSDploy yet, you will need to add ``--pre``, otherwise ``pip`` will refuse to install it.


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
