Configuring a jailhost
======================

Once the host has been successfully bootstrapped, we are left with a vanilla FreeBSD installation with the following exceptions:

- we have key based SSH access as root
- Python has been installed

But before we can create and manage jails, a few tasks still remain, in particular

- installation and configuration of ``ezjail``
- ZFS setup and layout, including optional encryption
- jail specific network setup

Unlike bootstrapping, this final step is implemented using ansible playbooks and has been divided into multiple roles, so all that is left for us is to apply the ``configure`` to the ``ez-master`` instance, i.e. like so::

	ploy configure ploy-demo

Among other things, this will create an additional zpool named ``tank`` (by default) which will be used to contain the jails.


Configuring as non-root
-----------------------

While bootstrapping currently *must* be performed as ``root`` (due to the fact that mfsBSD itself requires root login) some users may not want to enable root login for their systems.

If you want to manage a jailhost with a non-root user, you must perform the following steps manually:

- install ``sudo`` on the jailhost
- create a user account and enable SSH access for it
- enable passwordless ``sudo`` access for it
- disable SSH login for root (currently, automatically enabled during bootstrapping)

Additionally, you *must* configure the system using a playbook (i.e. simply assigning one or more roles won't work in this case) and in that playbook you must set the username and enable ``sudo``, i.e. like so:

.. code-block:: yaml

    ---
    - hosts: jailhost
      user: tomster
      sudo: yes
      roles:
        # apply the built-in bsdploy role jails_host
        - jails_host

And, of course, once bootstrapped, you need to set the same username in ``ploy.conf``:

.. code-block:: ini

    [ez-master:jailhost]
    user = tomster


Full-Disk encryption with GELI
------------------------------

One of the many nice features of FreeBSD is its `modular, layered handling of disks (GEOM) <http://www.freebsd.org/doc/handbook/geom.html>`_.
This allows to inject a crypto layer into your disk setup without that higher up levels (such as ZFS) need to be aware of it, which is exactly what BSDploy supports.

If you add ``bootstrap-geli = yes`` to an ``ez-master`` entry, BSDploy will generate a passphrase, encrypt the GEOM provider for the ``tank`` zpool and write the passphrasse to ``'/root/geli-passphrase`` and configures the appropriate ``geli_*_flag`` entries in ``rc.conf`` so that it is used automatically during booting.

The upshot is that when enabling GELI you still will have the same convenience as without encryption but can easily up the ante by removing the passphrase file (remember to keep it safe, though!). You will, however, need to attach the device manually after the system has booted and enter the passphrase.


Additional host roles
---------------------


The main bulk of work has been factored into the role ``jails_host`` which also is the default role.

If the network of your host is configured via DHCP you can apply an additional role named ``dhcp_host`` which takes care of the hosts sshd configuration when the DHCP lease changes.
To have it applied when calling ``configure`` add an explicit ``roles`` parameter to your ``ez-instance``:

.. code-block:: ini
    :emphasize-lines: 3-5

	[ez-master:ploy-demo]
	[...]
	roles =
		dhcp_host
		jails_host
	[...]

Technically, BSDploy injects its own roles to ansibles playbook path, so to apply your own custom additions, add additional roles to a top-level directory named ``roles`` and include them in your configuration and they will be applied as well.

Common tasks for such additional setup could be setting up a custom ZFS layout, configuring snapshots and backups, custom firewall rules etc, basically anything that you would not want to lock inside a jail.


.. note:: Curently, the ``jails_host`` playbook is rather monolithic, but given the way ansible works, there is the possibility of making it more granular, i.e. by tagging and/or parametrisizing specific sub-tasks and then to allow applying tags and parameter values in ``ploy.conf``.
