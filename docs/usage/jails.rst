Managing jails
==============

The life cycle of a jail managed by BSDploy begins with an ``instance`` entry in ``ploy.conf``, i.e. like so::

    [instance:webserver]
    ip = 10.0.0.1
    master = ploy-demo

The minimally required parameters are the IP address of the jail (``ip``) and a reference to the jailhost (``master``) – the name of the jail is taken from the section name (in the example ``webserver``).

.. note:: Unlike ``ez-master`` or other instances, names of jails are restricted by the constraints that FreeBSD imposes, namely they cannot contain dashes (``-``)

BSDploy creates its own loopback device (``lo1``) during configuration and assigns a network of ``10.0.0.0/8`` by default (see ``bsdploy/roles/jails_host/defaults/main.yml`` for other values and their defaults), so you can use any ``10.x.x.x`` IP address out-of-the-box for your jails.

Once defined, you can start the jail straight away. There is no explicit ``create`` command, if the jail does not exist during startup, it will be created on-demand::

	# ploy start webserver
	INFO: Creating instance 'webserver'
	INFO: Starting instance 'webserver' with startup script, this can take a while.

You can find out about the state of a jail by running ``ploy status JAILNAME``. 

A jail can be stopped with  ``ploy stop JAILNAME``.

A jail can be completely removed with ``ploy terminate JAILNAME``.  This will destroy the ZFS filesystem specific to that jail.


SSH Access
----------

BSDploy encourages jails to have a private IP address but compensates for that by providing convenient SSH access to them anyway, by automatically configuring an SSH ProxyCommand.

Essentially, this means that you can SSH into any jail (or other instance) by providing it as a target for ploy's ``ssh`` command, i.e.::

	# ploy ssh webserver
	FreeBSD 9.2-RELEASE (GENERIC) #6 r255896M: Wed Oct  9 01:45:07 CEST 2013

	Gehe nicht über Los.
	root@webserver:~ # 

Strictly speaking, you would need to address the jail instance together with the name of the host (to disambiguate multi-host scenarios) but since in this example there is only one jail host defined, ``webserver`` is enough, otherwise you would use ``jailhost-webserver``.


rsync and scp
*************

To access a jail with ``rsync`` (don't forget to install the ``rsync`` package into it!) or ``scp`` you can pass the ``ploy-ssh`` script into them like so::

	scp -S ploy-ssh some.file webserver:/some/path/
	rsync -e ploy-ssh some/path webserver:/some/path
