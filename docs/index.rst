BSDploy – FreeBSD jail provisioning
===================================

BSDploy is a comprehensive tool to **provision**, **configure** and **maintain** `FreeBSD <http://www.freebsd.org>`_ `jail hosts and jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails-intro.html>`_.

Its main design goal is to lower the barrier to *repeatable jail setups*.

Instead of performing updates on production hosts you are encouraged to update the *description* of your setup, test it against an identically configured staging scenario until it works as expected and then apply the updated configuration to production with confidence.

.. warning:: BSDploy is currently still in beta. While it's not considered ready for production, it is now in feature freeze mode and you are encouraged to :doc:`give it a spin </quickstart>` and `report any issues <http://github.com/tomster/bsdploy/issues>`_ that you find, so it can move to a 1.0 release – thanks!


Main Features
-------------

- **bootstrap** complete jail hosts from scratch

- create new jails by adding two or more lines to your configuration file and running ``ploy start``

- **declarative configuration** – all hosts and their properties defined in ``ploy.conf`` are automatically exposed to `Ansible <http://ansible.cc>`_. Run existing playbooks with ``ploy playbook`` or directly assign roles in ``ploy.conf`` and apply them using ``ploy configure``.

- **imperative maintenance**  – run `Fabric <http://fabfile.org>`_ scripts with ``ploy do JAILNAME TASKNAME`` and have all of the hosts and their variables at your disposal in ``fab.env``.

- configure `ZFS pools and filesystems <https://wiki.freebsd.org/ZFS>`_ with `whole-disk-encryption <http://www.freebsd.org/doc/handbook/disks-encrypting.html>`_

-  out-of-the-box support for `Virtualbox <https://www.virtualbox.org>`_ and `Amazon EC2 <http://aws.amazon.com>`_ with a plugin-architecture to support more easily.


Best of both worlds
*******************

As it turns out, combining a declarative approach to set up the initial state of a system combined with an imperative approach to provide maintenance operations on that state works really well.

Since the imperative scripts have the luxury of running against a well-defined context you can keep them short and concise without worrying about all those edge cases.

And since the playbooks needn't concern themselves with performing updates or other tasks you don't have to litter them with states such as ``restarted`` or ``updated`` or with non-states such as ``shell`` commands.


Under the hood
**************

Since BSDploy's scope is quite ambitious it naturally does not attempt do all of the work on its own. In fact, BSDPloy is just a fairly thin, slightly opinionated wrapper around existing, excellent tools. In addition to the above mentioned Ansible and Fabric, it uses `ezjail <http://erdgeist.org/arts/software/ezjail/>`_ on the host to manage the jails and numerous members of the `mr.awsome family <http://mrawsome.readthedocs.org/en/latest/>`_ for pretty much everything else.


Server requirements
*******************

A FreeBSD system that wants to be managed by BSDploy will need to have `ezjail <http://erdgeist.org/arts/software/ezjail/>`_ installed, as well as `Python <http://python.org>`_ and must have SSH access enabled (either for root or with ``sudo``).

BSDPloy can take care of these requirements for you during bootstrapping but of course you can also use it to manage existing machines that meet those three requirements.

BSDPloy currently only supports FreeBSD 9.2 (although in theory any 9.x should work) but not yet FreeBSD 10. But that is only a matter of time. We can't wait to use it on 10 ourselves :-)


Client requirements
*******************

BSDploy and its dependencies are written in `Python <http://python.org>`_ and thus should run on pretty much any platform, although it's currently only been tested on Mac OS X and FreeBSD.


Contents:
---------

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   narr/provisioning
   narr/provisioning-plain
   narr/bootstrapping
   narr/staging
   narr/updating


Contribute
----------

Code and issues are hosted at github:

- Issue Tracker: http://github.com/tomster/bsdploy/issues
- Source Code: http://github.com/tomster/bsdploy
- IRC: the developers can be found on #bsdploy on freenode.net


License
-------

The project is licensed under the Beerware license.


TODO
----

The following features already exist but still need to be documented:

- provisioning + bootstrapping
   - plain instances (a.k.a. 'iron')
   - EC2 (daemonology based)
   - hetzner (mfsBSD based)
   - VirtualBox (mfsBSD based)
   - pre-configured SSH server keys
   - enabling full-disk encryption (GELI)
- configuration
- creating a jailhost
- creating jails
- jail access
   - proxy command
   - port forwarding
   - public IP
- ansible support
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
- Licence
- support vmware?
