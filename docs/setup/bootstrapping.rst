Bootstrapping
=============

Bootstrapping in the context of BSDploy means installing FreeBSD onto a :doc:`previously provisioned host<overview>` and the smallest amount of configuration to make it ready for its final configuration.

The Bootstrapping process assumes that the target host has been booted into an installer and can be reached via SSH under the configured address and that you have configured the appropriate bootstrapping type (currently either ``mfsbsd`` or ``daemonology``).


Bootstrapping FreeBSD 9.x
-------------------------

The default version that BSDploy assumes is 10.3.
If you want to install different versions, i.e. 9.2 you must:

- use the iso image for that version::

    % ploy-download http://mfsbsd.vx.sk/files/iso/9/amd64/mfsbsd-se-9.2-RELEASE-amd64.iso 4ef70dfd7b5255e36f2f7e1a5292c7a05019c8ce downloads/

- set ``bootstrap-host-key`` in ``ploy.conf`` to content of ``/etc/ssh/ssh_host_rsa_key.pub`` in the mfsbsd image
  (each mfsbsd release has it's own hardcoded ssh host key)
- create a file named ``files.yml`` in ``bootstrap-files`` with the following contents:

  .. code-block:: yaml

    ---
    'pkg.txz':
        url: 'http://pkg.freebsd.org/freebsd:9:x86:64/quarterly/Latest/pkg.txz'
        directory: '/mnt/var/cache/pkg/All'
        remote: '/mnt/var/cache/pkg/All/pkg.txz'


Bootstrap configuration
-----------------------

Since bootstrapping is specific to BSDploy we cannot configure it in the provisioning instance. Instead we need to create a specific entry for it in our configuration of the type ``ez-master`` and assign it to the provisioner.

I.e. in our example:

.. code-block:: ini

    [ez-master:jailhost]
    instance = ploy-demo


Required parameters
+++++++++++++++++++

The only other required value for an ``ez-master`` besides its provisioner is the name of the target device(s) the system should be installed on.

If you don't know the device name FreeBSD has assigned, run ``gpart list`` and look for in the ``Consumers`` section towards the end of the output. 

If you provide more than one device name, BSDploy will create a zpool mirror configuration, just make sure the devices are compatible.

There we can provide the name of the target device, so we get the following:

.. code-block:: ini

    [ez-master:jailhost]
    instance = ploy-demo
    bootstrap-system-devices = ada0

Or if we have more than one device:

.. code-block:: ini

    [ez-master:jailhost]
    instance = ploy-demo
    bootstrap-system-devices =
        ada0
        ada1


Optional parameters
+++++++++++++++++++

You can use the following optional parameters to configure the bootstrapping process and thus influence what the jail host will look like:

- ``bootstrap-system-pool-size``: BSDploy will create a zpool on the target device named ``system`` with the given size. This value will be passed on to ``zfsinstall``, so you can provide standard units, such as ``5G``. Default is ``20G``.

- ``bootstrap-swap-size``: This is the size of the swap space that will be created. Default is double the amount of detected RAM.

- ``bootstrap-bsd-url``: If you don't want to use the installation files found on the installer image (or if your boot image doesn't contain any) you can provide an explicit alternative (i.e. ``http://ftp4.de.freebsd.org/pub/FreeBSD/releases/amd64/9.2-RELEASE/``) and this will be used to fetch the system from.

- ``bootstrap-host-key``: Since the installer runs a different sshd configuration than the final installation, we need to provide its ssh host key explicitly. However, if you don't provide one, BSDploy will assume the (currently hardcoded) host key of the 10.3 mfsBSD installer . If you are using newer versions you must update the value to the content of ``/etc/ssh/ssh_host_rsa_key.pub`` in the mfsbsd image.

- ``firstboot-update``: By default bootstrapping will install and enable the `firstboot-freebsd-update <http://www.freshports.org/sysutils/firstboot-freebsd-update/>`_ package. This will update the installed system automatically (meaning non-interactively) to the latest patchlevel upon first boot. If for some reason you do not wish this to happen, you can disable it by setting this value to ``false``.

- ``http_proxy``: If set, that proxy will be used for all ``pkg`` operations performed on that host, as well as for downloading any assets during bootstrapping (``base.tbz`` etc.)


.. note:: Regarding the http proxy setting it is noteworthy, that ``pkg`` servers have rather restrictive caching policies in their response headers, so that most proxies' default configurations will produce misses. Here's an example for how to configure squid to produce better results:

    .. code-block:: sh

        # match against download urls for specific packages - their content never changes for the same url, so we cache aggressively
        refresh_pattern -i (quarterly|latest)\/All\/.*(\.txz) 1440 100% 1051200 ignore-private ignore-must-revalidate override-expire ignore-no-cache
        # match against meta-information - this shouldn't be cached quite so aggressively
        refresh_pattern -i (quarterly|latest)\/.*(\.txz) 1440 100% 10080 ignore-private ignore-must-revalidate override-expire ignore-no-cache

    Also you will probably want to adjust the following:

    .. code-block:: sh

        maximum_object_size_in_memory 32 KB
        maximum_object_size 2000 MB


Bootstrap rc.conf
-----------------

A crucial component of bootstrapping is configuring ``/etc/rc.conf``.

One option is to provide a custom rc.conf (verbatim or as a template) for your host via :ref:`bootstrap-files`.

But often times, the default template with a few additional custom lines will suffice.

Here's what the default ``rc.conf`` template looks like:

.. literalinclude:: ../../bsdploy/bootstrap-files/rc.conf

This is achieved by providing ``boostrap-rc-xxxx`` key/values in the instance definition in ``ploy.conf``.


.. _bootstrap-files:

Bootstrap files
---------------

During bootstrapping a certain number of files are copied onto the target host.

Some of these files...

- need to be provided by the user (i.e. ``authorized_keys``)
- others have some (sensible) defaults (i.e. ``rc.conf``)
- some can be downloaded via URL (i.e.) ``http://pkg.freebsd.org/freebsd:10:x86:64/latest/Latest/pkg.txz``

The list of files, their possible sources and their destination is encoded in a ``.yml`` file, the default of which is this

.. literalinclude:: ../../bsdploy/bootstrap-files/files.yml

.. warning:: Overriding the list of default files is an advanced feature and in most cases it is not needed. Also keep in mind that bootstrapping is only about getting the host ready for running BSDploy. Any additional files beyond that should be uploaded lateron via fabric and/or playbooks.

It is however, quite common and useful to customize files that are part of the above list with custom versions *per host*.

For example, to create a custom ``rc.conf`` for a particular instance, create a ``bootstrap-files`` entry for it and point it to a directory in your project, usually ``../bootstrap-files/INSTANCENAME/`` and place your version of ``rc.conf`` inside there. Note, that by default this file is rendered as a template, your custom version will be, too.

Any file listed in the YAML file found inside that directory will take precedence during bootstrapping, but any file *not* found in there will be uploaded from the default location instead.

Files encrypted using ``ploy vault encrypt`` are recognized and decrypted during upload.

SSH host keys are generated locally via ``ssh-keygen`` and stored in ``bootstrap-files``.
If your ``ssh-keygen`` doesn't support a key type (like ecdsa on OS X), then the key won't be created and FreeBSD will create it during first boot.
The generated keys are used to verify the ssh connection, so it is best to add them into version control.
Since the private ssh keys are sensitive data, you should encrypt them using ``ploy vault encrypt ...`` before adding them into version control.


Bootstrap execution
-------------------

With (all) those pre-requisites out of the way, the entire process boils down to issuing the following command::

    % ploy bootstrap

Or, if your configuration has more than one instance defined you need to provide its name, i.e.::

    % ploy bootstrap jailhost

Once this has run successfully, you can move on to the final setup step :doc:`Configuration <configuration>`.
