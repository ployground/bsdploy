Configuring a jailhost
======================

Once the host has been successfully bootstrapped, we are left with a vanilla FreeBSD installation with the following exceptions:

- we have key based SSH access as root
- Python has been installed

But before we can create and manage jails, a few tasks still remain, in particular

- installation and configuration of ``ezjail``
- ZFS setup and layout
- jail specific network setup

Unlike bootstrapping, this final step is implemented using ansible playbooks and has been divided into multiple roles, so all that is left for us is to apply the ``configure`` to the ``ez-master`` instance, i.e. like so::

	ploy configure ploy-demo


Additional host roles
---------------------


The main bulk of work has been factored into the role ``jails_host`` which also is the default role.

If the network of your host is configured via DHCP you can apply an additional role named ``dhcp_host`` which takes care of the hosts sshd configuration when the DHCP lease changes. To have it applied when calling ``configure`` add an explicit ``roles`` parameter to your ``ez-instance``:

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
