bsdploy – FreeBSD jail provisioning
===================================

BSDploy is a comprehensive tool to **provision**, **configure** and **maintain** `FreeBSD <http://www.freebsd.org>`_ `jail hosts and jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails-intro.html>`_.


Main Features
-------------

- **bootstrap** complete jail hosts from scratch

- configure `ZFS pools and filesystems <https://wiki.freebsd.org/ZFS>`_ with `whole-disk-encryption <http://www.freebsd.org/doc/handbook/disks-encrypting.html>`_

-  out-of-the-box support for `Virtualbox <https://www.virtualbox.org>`_ and `Amazon EC2 <http://aws.amazon.com>`_.

- create new jails by adding two or more lines to your configuration file and running ``ploy start``

- **declarative configuration** – all hosts and their properties defined in ``ploy.conf`` are automatically exposed to `Ansible <http://ansible.cc>`_. Run existing playbooks with ``ploy playbook`` or directly assign roles in ``ploy.conf`` and apply them using ``ploy configure``.

- **imperative maintenance**  – run `Fabric <http://fabfile.org>`_ scripts with ``ploy do JAILNAME TASKNAME`` and have all of the hosts and their variables at your disposal in ``fab.env``.


Best of both worlds
*******************

Those last two items bear repeating: it turns out, that combining a declarative approach to set up the initial state of a system combined with an imperative approach to provide maintenance operations on that state works really well. And since the imperative scripts have the luxury of running against a well-defined context you can keep them short and concise without worrying about all those edge cases.


Under the hood
**************

Since BSDploy's scope is quite ambitious it naturally does not attempt do all of the work on its own. In fact, BSDPloy is just a fairly thin, slightly opinionated wrapper around existing, excellent tools. In addition to the above mentioned Ansible and Fabric, it uses `ezjail <http://erdgeist.org/arts/software/ezjail/>`_ on the host to manage the jails and numerous members of the `mr.awsome family <http://mrawsome.readthedocs.org/en/latest/>`_ for pretty much everything else.


Server requirements
*******************

A FreeBSD system that wants to be managed by BSDploy will need to have `ezjail <http://erdgeist.org/arts/software/ezjail/>`_ installed, as well as `Python <http://python.org>`_ and must have SSH access enabled (either for root or with ``sudo``).

BSDPloy can take care of these requirements for you during bootstrapping but of course you can also use it to manage existing machines that meet those three requirements.

BSDPloy currently only supports FreeBSD 9.2 (although in theory any 9.x should work) but not yet FreeBSD 10. But that is only a matter of time. We can't wait to use it on 10 ourselves :-)


Contents:
---------

.. toctree::
   :maxdepth: 2

   installation


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

