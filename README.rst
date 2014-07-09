BSDploy – FreeBSD jail provisioning
===================================

BSDploy is a comprehensive tool to **provision**, **configure** and **maintain** `FreeBSD <http://www.freebsd.org>`_ `jail hosts and jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails-intro.html>`_.

Its main design goal is to lower the barrier to *repeatable jail setups*.

Instead of performing updates on production hosts you are encouraged to update the *description* of your setup, test it against an identically configured staging scenario until it works as expected and then apply the updated configuration to production with confidence.

Main Features
-------------

- **bootstrap** complete jail hosts from scratch

- create new jails by adding two or more lines to your configuration file and running ``ploy start``

- **declarative configuration** – all hosts and their properties defined in ``ploy.conf`` are automatically exposed to `Ansible <http://ansible.cc>`_. Run existing playbooks with ``ploy playbook`` or directly assign roles in ``ploy.conf`` and apply them using ``ploy configure``.

- **imperative maintenance**  – run `Fabric <http://fabfile.org>`_ scripts with ``ploy do JAILNAME TASKNAME`` and have all of the hosts and their variables at your disposal in ``fab.env``.

- configure `ZFS pools and filesystems <https://wiki.freebsd.org/ZFS>`_ with `whole-disk-encryption <http://www.freebsd.org/doc/handbook/disks-encrypting.html>`_

-  **modular provisioning** with plugins for `VirtualBox <https://www.virtualbox.org>`_ and `Amazon EC2 <http://aws.amazon.com>`_ and an architecture to support more.


Best of both worlds
*******************

Combining a declarative approach for setting up the initial state of a system combined with an imperative approach for providing maintenance operations on that state has significant advantages:

1. Since the imperative scripts have the luxury of running against a well-defined context, you can keep them short and concise without worrying about all those edge cases.

2. And since the playbooks needn't concern themselves with performing updates or other tasks you don't have to litter them with awkward states such as ``restarted`` or ``updated`` or – even worse – with non-states such as ``shell`` commands.


Under the hood
**************

BSDploy's scope is quite ambitious, so naturally it does not attempt to do all of the work on its own. In fact, BSDPloy is just a fairly thin, slightly opinionated wrapper around existing excellent tools.

In addition to the above mentioned Ansible and Fabric, it uses `ezjail <http://erdgeist.org/arts/software/ezjail/>`_ on the host to manage the jails and on the client numerous members of the `ployground family <https://github.com/ployground/>`_ for pretty much everything else.


Full documentation
------------------

The full documentation is `hosted at RTD <http://docs.bsdploy.net>`_.
