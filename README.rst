BSDploy is a tool to deploy `FreeBSD <http://www.freebsd.org>`_ `jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails-intro.html>`_.

Not wanting to re-invent the wheel, under the hood it uses `mr.awsome <https://pypi.python.org/pypi/mr.awsome>`_ for provisioning, `ansible <http://ansible.cc>`_ for configuration and `fabric <http://fabfile.org>`_ for maintenance.


Features
========

 - configure multiple hosts and jails in one canonical ini-file
 - bootstrap complete jail hosts from scratch - both virtual machines, as well as physical ones. ``bsdploy`` will take care of installing FreeBSD for you, including configuration of `ZFS pools <https://wiki.freebsd.org/ZFS>`_ and even encrypts them using `GELI <http://www.freebsd.org/doc/handbook/disks-encrypting.html>`_.
 - create new jails simply by adding two or more lines to your configuration file and running ``ploy start`` – bsdploy will take care of configuring the required IP address on the host
 - **ansible support** – no more mucking about with host files: all hosts and their variables defined in ``ploy.conf`` are automatically exposed to ansible. Run them with ``ploy playbook path/to/playbook.yml``.
 - ditto for **Fabric** – run fabric scripts with ``ploy do JAILNAME TASKNAME`` and have all your hosts and their variables at your disposal in ``fab.env``.
 - jails receive private IP addresses by default, so they are not reachable from the outside - for configuration access (i.e. applying ansible playbooks to them or running fabric scripts inside of them) bsdploy transparently configures SSH ProxyCommand based access.
 - Easily configure ``ipnat`` on the jail host to white-list access from the outside – this greatly reduces the chance of accidentally exposing services to the outside world that shouldn't be.
 - **Amazon EC2** support – provision and configure jailhosts on EC2.

With bsdploy you can create and configure one or more jail hosts with one or more jails inside them, all configured in one canonical ``ini`` style configuration file (by default in ``etc/ploy.conf)``::

    [ez-master:vm-master]
    host = 127.0.0.1
    port = 47022

    [ez-instance:webserver]
    ip = 10.0.0.2
    fqdn = test.local
    fabfile = deployment/webserver.py

    [ez-instance:database]
    ip = 10.0.0.3
    dbname = production

    [ez-instance:application]
    ip = 10.0.0.4
    version = 1.2.3


Examples
========

To give it a spin, best `check out the example repository <https://github.com/tomster/ezjail-test-vm>`_.


Development
===========

To develop ``bsdploy`` itself use the provided Makfile – running ``make`` will install a development version of itself and its direct dependencies (i.e. the ``mr.awsome.*`` packages).


TODO
====

 - documentation *cough*
 - include poudriere support
 - make the private network for the jails configurable (the hard coded 10.0.0.x is not always desirable)


 Misc
 ====

 Miscellaneous notes that should eventually make their way into the proper documentation.

 Selectively applying jailhost configuration
 +++++++++++++++++++++++++++++++++++++++++++

``ploy configure-jailhost`` applies the ``jails_host`` role (see ``roles/jails_host``.  if you don't want to apply it wholesale or want to re-apply certain tags of it, you can use a top-level playbook like so::

    - hosts: my-jailhost
      user: root
      roles:
        - { role: jails_host, tags: ['configure'] }

i.e. to then only update the ipnat rules, do this::

     bin/ploy playbook staging.yml -t configure -t ipnat_rules

the 'trick' is to use multiple tags to narrow down the tasks to only what you need.
