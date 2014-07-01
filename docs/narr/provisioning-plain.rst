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


Download installer image
************************

First, you need to download the installer image and copy it onto a suitable medium, i.e. an USB stick.

As mentioned in the quickstart, BSDploy provides a small cross-platform helper for downloading assets via HTTP which also checks the integrity of the downloaded file::

	mkdir downloads
	ploy-download http://mfsbsd.vx.sk/files/images/9/amd64/mfsbsd-se-9.2-RELEASE-amd64.img 9f354d30fe5859106c1cae9c334ea40852cb24aa downloads/


Creating a bootable USB medium (Mac OSX)
****************************************

For the time being we only provide instructions for Mac OS X, sorry! If you run Linux you probably already know how to do this, anyway :-)

- Run ``diskutil list`` to see which drives are currently in your system.
- insert your medium
- re-run ``diskutil list`` and notice which number it has been assigned (N)
- run ``diskutil unmountDisk /dev/diskN``
- run ```sudo dd if=downloads/mfsbsd-se-9.2-RELEASE-amd64.img of=/dev/diskN bs=1m``
- run ``diskutil unmountDisk /dev/diskN``

Insert the USB stick into the *target host* and boot from it. Log in as ``root`` using the pre-configured password ``mfsroot``. Either note the name of the ethernet interface and the IP address it has been given by running ``ifconfig`` or set them to the desired values in ``/etc/rc.conf`` if you do not have a DHCP environment.

Run ``gpart list`` and note the device name of the hard drive(s). Enter this values into your ``ploy.conf``.


Hetzner
-------

How to provision a dedicated machine hosted at Hetzner using their rescue system.

