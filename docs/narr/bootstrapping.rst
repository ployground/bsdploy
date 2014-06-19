Bootstrapping
=============

Bootstrapping in the context of BSDploy means installing FreeBSD onto a :doc:`previously provisioned host<provisioning>` and the smallest amount of configuration to make it ready for its final configuration.

The Bootstrapping process assumes that the target host has been booted into a installer and can be reached via SSH under the configured address and that you have configured the appropriate bootstrapping type (currently either ``mfsbsd`` or ``daemonology``).

With those pre-requisites out of the way, the entire process boils down to issuing the following command::

	ploy bootstrap

Or, if your configuration has more than one instance defined you need to provide its name, i.e.::

	ploy bootstrap demo-server


Bootstrap rc.conf
-----------------

A crucial component of bootstrapping is configuring ``/etc/rc.conf``.

One option is to provide a custom rc.conf (verbatim or as a template) for your host via :ref:`bootstrap-files`.

But often times, the default template with a few additional custom lines will suffice.

Here's what the default ``rc.conf`` template looks like:

.. literalinclude:: ../../bootstrap-files/rc.conf

This is achieved by providing ``boostrap-rc-xxxx`` key/values in the instance definition in ``ploy.conf``.


.. _bootstrap-files:

Bootstrap files
---------------

TBD