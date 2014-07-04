Managing jails
==============

The life cycle of a jail manage by BSDploy begins with an entry in ``ploy.conf``, i.e. like so::

    [instance:webserver]
    ip = 10.0.0.1
    master = ploy-demo

The minimally required parameter is the IP address of the jail (``ip``) and a reference to the jailhost (``master``).

BSDploy creates its own loopback device (``lo1``) during configuration and assigns a network of ``10.0.0.0/8`` by default (see ``bsdploy/roles/jails_host/defaults/main.yml`` for other values and their defaults), so you can use any ``10.x.x.x`` IP address out-of-the-box for your jails.

Once defined, you can start the jail straight away. There is no explicit ``create`` command, if the jail does not exist during startup, it will be created on-demand::

	ploy start webserver

You can find out about the state of a jail by running ``ploy status JAILNAME``. In addtition there are also ``stop`` and ``terminate`` which do exactly what you think they do :)
