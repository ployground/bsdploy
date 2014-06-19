Plain instances
===============

The most simple provider simply assumes an already existing instance. Here any configuration is purely descriptive. Unlike with the other providers we tell BSDploy how things are and it doesn't do anything about it.

For example::

	[plain-instance:home-server]
	host = 10.0.1.2
	fingerprint = 91:e7:4b:30:0d:b5:ea:b9:f9:eb:8a:a0:44:ab:bd:01

At the very least you will need to provide a ``host`` (IP address or hostname) and its SSH ``fingerprint``.

Additionally, you can provide a non-default SSH ``port`` and a ``user`` to connect with (default is ``root``).


Local hardware
--------------

How to provision a FreeBSD compatible PC that you have physical access to.


Hetzner
-------

How to provision a dedicated machine hosted at Hetzner using their rescue system.

