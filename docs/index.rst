.. include:: ../README.rst

.. warning:: BSDploy is currently still in beta. While it's not considered ready for production, it is now in feature freeze mode and you are encouraged to :doc:`give it a spin </quickstart>` and `report any issues <http://github.com/ployground/bsdploy/issues>`_ that you find, so it can move to a 1.0 release – thanks!


Dive in
-------

.. toctree::
   :maxdepth: 2

   installation
   quickstart


Setup
-----

How to setup a host from scratch or make an existing one ready for BSDploy:

.. toctree::
   :maxdepth: 2

   setup/overview
   setup/provisioning-plain
   setup/provisioning-virtualbox
   setup/bootstrapping
   setup/configuration


General usage
-------------

How to create an manage jails once the host is set up:

.. toctree::
   :maxdepth: 2

   usage/jails
   usage/ansible
   usage/fabric


Special use cases
-----------------

.. toctree::
   :maxdepth: 2

   advanced/staging
   advanced/updating


Contribute
----------

Code and issues are hosted at github:

- Issue Tracker: http://github.com/ployground/bsdploy/issues
- Source Code: http://github.com/tomster/bsdploy
- IRC: the developers can be found on #bsdploy on freenode.net


License
-------

The project is licensed under the Beerware license.


TODO
----

The following features already exist but still need to be documented:

- provisioning + bootstrapping
   - EC2 (daemonology based)
   - pre-configured SSH server keys
- jail access
   - port forwarding
   - public IP
- fabric support
- combining ansible and fabric
- ZFS management
- Creating and restoring ZFS snapshots
- poudriere support
- Upgrading strategies
- 'vagrant mode' (use - virtualized - jails as development environment)

The following features don't exist yet but should eventually :)

- OS installers
   - homebrew
   - freebsd ports + pkgng
   - ?
- support ``bootstrap-rc-XXX``
- support vmware explicitly (like virtualbox)?
