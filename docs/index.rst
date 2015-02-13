.. include:: ../README.rst


.. warning::
   BSDploy is  intended to be used to set up *new* hosts that will then be fully managed by it.
   While technically possible, it is *not* intended to be run against or to manage existing systems
   that have been bootstrapped without BSDploy.
   Running BSDploy against hosts that have not been bootstrapped by it can result in loss of data.

Dive in
-------

.. toctree::
   :maxdepth: 2

   installation
   quickstart


Tutorial
--------

A more in-depth tutorial than the quickstart.

.. toctree::
   :maxdepth: 2

   tutorial/overview
   tutorial/webserver
   tutorial/transmission
   tutorial/staging


Setup
-----

How to setup a host from scratch or make an existing one ready for BSDploy:

.. toctree::
   :maxdepth: 2

   setup/overview
   setup/provisioning-plain
   setup/provisioning-virtualbox
   setup/provisioning-ec2
   setup/bootstrapping
   setup/configuration


General usage
-------------

How to create and manage jails once the host is set up:

.. toctree::
   :maxdepth: 2

   usage/jails
   usage/ansible
   usage/fabric
   usage/ansible-with-fabric


Special use cases
-----------------

.. toctree::
   :maxdepth: 2

   advanced/staging
   advanced/updating
   advanced/customizing-bootstrap


Contribute
----------

Code and issues are hosted at github:

- Issue Tracker: http://github.com/ployground/bsdploy/issues
- Source Code: http://github.com/ployground/bsdploy
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
- ZFS management
- Creating and restoring ZFS snapshots
- poudriere support
- Upgrading strategies
- 'vagrant mode' (use - virtualized - jails as development environment)

The following features don't exist yet but should eventually :)

- OS installers
   - homebrew
- support vmware explicitly (like virtualbox)?
