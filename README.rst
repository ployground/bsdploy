BSDploy – FreeBSD jail provisioning
===================================

BSDploy is a comprehensive tool to remotely **provision**, **configure** and **maintain** `FreeBSD <http://www.freebsd.org>`_ `jail hosts and jails <http://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/jails.html>`_.

Its main design goal is to lower the barrier to *repeatable jail setups*.

Instead of performing updates on production hosts you are encouraged to update the *description* of your setup, test it against an identically configured staging scenario until it works as expected and then apply the updated configuration to production with confidence.


Main Features
-------------

- **provision** complete jail hosts from scratch

- **describe** one or more jail hosts and their jails in a canonical configuration

- **declarative configuration** – apply `Ansible <http://ansible.com>`_ playbooks to hosts and jails

- **imperative maintenance**  – run `Fabric <http://fabfile.org>`_ scripts against hosts and jails

- configure `ZFS pools and filesystems <https://wiki.freebsd.org/ZFS>`_ with `whole-disk-encryption <http://www.freebsd.org/doc/handbook/disks-encrypting.html>`_

-  **modular provisioning** with plugins for `VirtualBox <https://www.virtualbox.org>`_ and `Amazon EC2 <http://aws.amazon.com>`_ and an architecture to support more.


How it works
------------

BSDploy takes the shape of a commandline tool by the name of ``ploy`` which is installed on a so-called *control host* (typically your laptop or desktop machine) with which you then control one or more *target hosts*. The only two things installed on target hosts by BSDploy are Python and ``ezjail`` – everything else stays on the control host.


Example Session
---------------

Here's what an abbreviated bootstrapping session of a simple website inside a jail on an Amazon EC2 instance could look like::

    # ploy start ec-instance
    [...]
    # ploy configure jailhost
    [...]
    # ploy start webserver
    [...]
    # ploy configure webserver
    [...]
    # ploy do webserver upload_website


Best of both worlds
-------------------

Combining a declarative approach for setting up the initial state of a system with an imperative approach for providing maintenance operations on that state has significant advantages:

1. Since the imperative scripts have the luxury of running against a well-defined context, you can keep them short and concise without worrying about all those edge cases.

2. And since the playbooks needn't concern themselves with performing updates or other tasks you don't have to litter them with awkward states such as ``restarted`` or ``updated`` or – even worse – with non-states such as ``shell`` commands.


Under the hood
--------------

BSDploy's scope is quite ambitious, so naturally it does not attempt to do all of the work on its own. In fact, BSDPloy is just a fairly thin, slightly opinionated wrapper around existing excellent tools.

In addition to the above mentioned Ansible and Fabric, it uses `ezjail <http://erdgeist.org/arts/software/ezjail/>`_ on the host to manage the jails and on the client numerous members of the `ployground family <https://github.com/ployground/>`_ for pretty much everything else.


Full documentation
------------------

The full documentation is `hosted at RTD <http://docs.bsdploy.net>`_.
