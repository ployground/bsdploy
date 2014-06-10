bsdploy – FreeBSD jail provisioning
===================================

BSDploy is a tool to deploy `FreeBSD <http://www.freebsd.org>`_ `jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails-intro.html>`_.

Not wanting to re-invent the wheel, under the hood it uses `mr.awsome <https://pypi.python.org/pypi/mr.awsome>`_ for provisioning, `ansible <http://ansible.cc>`_ for configuration and `Fabric <http://fabfile.org>`_ for maintenance.


Features
--------

- configure multiple hosts and jails in one canonical ini-file

- bootstrap complete jail hosts from scratch - both virtual machines, as well as physical ones. ``bsdploy`` will take care of installing FreeBSD for you, including configuration of `ZFS pools <https://wiki.freebsd.org/ZFS>`_ and even encrypts them using `GELI <http://www.freebsd.org/doc/handbook/disks-encrypting.html>`_.

- create new jails simply by adding two or more lines to your configuration file and running ``ploy start`` – bsdploy will take care of configuring the required IP address on the host

- **ansible support** – no more mucking about with host files: all hosts and their variables defined in ``ploy.conf`` are automatically exposed to ansible. Run them with ``ploy playbook path/to/playbook.yml``.

- ditto for **Fabric** – run fabric scripts with ``ploy do JAILNAME TASKNAME`` and have all your hosts and their variables at your disposal in ``fab.env``.

- jails receive private IP addresses by default, so they are not reachable from the outside - for configuration access (i.e. applying ansible playbooks to them or running fabric scripts inside of them) bsdploy transparently configures SSH ProxyCommand based access.

- Easily configure ``ipnat`` on the jail host to white-list access from the outside – this greatly reduces the chance of accidentally exposing services to the outside world that shouldn't be.
- **Amazon EC2** support – provision and configure jailhosts on EC2.


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

