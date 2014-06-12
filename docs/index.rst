bsdploy – FreeBSD jail provisioning
===================================

BSDploy is a comprehensive tool to **provision**, **configure** and **maintaining** `FreeBSD <http://www.freebsd.org>`_ `jail hosts and jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails-intro.html>`_.


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

