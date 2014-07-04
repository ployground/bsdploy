Bootstrapping
=============

Bootstrapping in the context of BSDploy means installing FreeBSD onto a :doc:`previously provisioned host<provisioning>` and the smallest amount of configuration to make it ready for its final configuration.

The Bootstrapping process assumes that the target host has been booted into a installer and can be reached via SSH under the configured address and that you have configured the appropriate bootstrapping type (currently either ``mfsbsd`` or ``daemonology``).


Bootstrap configuration
-----------------------

Since bootstrapping is specific to BSDploy we cannot configure it in the provisioning instance. Instead we need to create a specific entry for it in our configuration of the type ``ez-master`` and assign it to the provisioner.

I.e. in our example::

    [ez-master:ploy-demo]
    instance = ploy-demo-provisioner


Required parameters
+++++++++++++++++++

The only other required value for an ``ez-master`` besides its provisioner is the name of the target device(s) the system should be installed on.

If you don't know the device name FreeBSD has assigned, run ``gpart list`` and look for in the ``Consumers`` section towards the end of the output. 

If you provide more than one device name, BSDploy will create a zpool mirror configuration, just make sure the devices are compatible.

There we can provide the name of the target device, so we get the following::

    [ez-master:ploy-demo]
    instance = ploy-demo-provisioner
    bootstrap-system-devices = ada0

Or if we have more than one device::

    [ez-master:ploy-demo]
    instance = ploy-demo-provisioner
    bootstrap-system-devices =
        ada0
        ada1


Optional parameters
+++++++++++++++++++

You can use the following optional parameters to configure the bootstrapping process and thus influence what the jail host will look like:

- ``bootstrap-system-pool-size``: BSDploy will create a zpool on the target device named ``system`` with the given size. This value will be passed on to ``zfsinstall``, so you can provide standard units, such as ``5G``. Default is ``20G``.

- ``bootstrap-swap-size``: This is the size of the swap space that will be created. Default is double the amount of detected RAM.

- ``bootstrap-bsd-url``: If you don't want to use the installation files found on the installer image (or if your boot image doesn't contain any) you can provide an explicit alternative (i.e. ``http://ftp4.de.freebsd.org/pub/FreeBSD/releases/amd64/9.2-RELEASE/``) and this will be used to fetch the system from.

- ``bootstrap-fingerprint``: Since the installer runs a different sshd configuration than the final installation, we need to provide its fingerprint explicitly. However, if you don't provide one, BSDploy will assume the (currently hardcoded) fingerprint of the 9.2 mfsBSD installer (``02:2e:b4:dd:c3:8a:b7:7b:ba:b2:4a:f0:ab:13:f4:2d``).


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

During bootstrapping a certain number of files are copied onto the target host.

.. warning:: Overriding the list of default files is an advanced feature. In most cases it is not needed. Also keep in mind that bootstrapping is only about getting the host ready for running BSDploy. Any additional files beyond that should be uploaded lateron via fabric and/or playbooks.

Some of these files...

- need to be provided by the user (i.e. ``authorized_keys``)
- others have some (sensible) defaults (i.e. ``rc.conf``)
- some can be downloaded via URL (i.e.) ``http://pkg.freebsd.org/freebsd:9:x86:64/latest/Latest/pkg.txz``

The list of files, their possible sources and their destination is encoded in a ``.yml`` file, the default of which is this

.. literalinclude:: ../../bootstrap-files/files.yml

For those which can be downloaded we check the ``downloads`` directory. If the file exists there
(and if the checksum matches TODO!) we will upload it to the host. If not, we will fetch the file
from the given URL from the host.

For files that cannot be downloaded (authorized_keys, rc.conf etc.) we allow the user to provide their
own version in a ``bootstrap-files`` folder. The location of this folder can either be explicitly provided
via the ``bootstrap-files`` key in the host definition of the config file or it defaults to ``bootstrap-files``.

User provided files can be rendered as Jinja2 templates, by providing ``use_jinja: True`` in the YAML file.
They will be rendered with the server configuration dictionary as context.

If the file is not found there, we revert to the default files that are part of bsdploy. If the file cannot be found there either we either error out or for authorized_keys we look in ``~/.ssh/identity.pub``.


Bootstrap execution
-------------------

With (all) those pre-requisites out of the way, the entire process boils down to issuing the following command::

    ploy bootstrap

Or, if your configuration has more than one instance defined you need to provide its name, i.e.::

    ploy bootstrap ploy-demo

Once this has run successfully, you can move on to the final setup step :doc:`Configuration <configuration>`.
