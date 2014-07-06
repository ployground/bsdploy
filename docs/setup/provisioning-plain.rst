Provisioning plain instances
============================

The most simple provider simply assumes an already existing host. Here any configuration is purely descriptive. Unlike with the other providers we tell BSDploy how things are and it doesn't do anything about it.

For example::

	[plain-instance:ploy-demo]
	host = 10.0.1.2

At the very least you will need to provide a ``host`` (IP address or hostname).

Additionally, you can provide a non-default SSH ``port`` and a ``user`` to connect with (default is ``root``).


Local hardware
--------------

The most common scenario for using a plain instance is physical hardware that you have access to and can boot from a custom installer medium.


Download installer image
************************

First, you need to download the installer image and copy it onto a suitable medium, i.e. an USB stick.

As mentioned in the quickstart, BSDploy uses `mfsBSD <http://mfsbsd.vx.sk>`_ which is basically the official FreeBSD installer plus pre-configured SSH access. Also, it provides a small cross-platform helper for downloading assets via HTTP which also checks the integrity of the downloaded file::

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
- now you can remove the stick and boot the target host from it


Booting into mfsBSD
*******************

Insert the USB stick into the *target host* and boot from it. Log in as ``root`` using the pre-configured password ``mfsroot``. Either note the name of the ethernet interface and the IP address it has been given by running ``ifconfig`` and (temporarily) set it in ``ploy.conf`` or configure them one-time to match your expectations.


One-Time manual network configuration
+++++++++++++++++++++++++++++++++++++

BSDploy needs to access the installer via SSH and it in turn will need to download assets from the internet during installation, so we need to configure the interface, the gateway, DNS and sshd.

In the above mentioned example that could be::

    ifconfig em0 netmask 255.255.255.0
    route add default 10.0.1.1

Since usually, the router also performs as DNS you would edit ``/etc/resolv.conf`` to look like so::

    nameserver 10.0.1.1

Finally restart sshd::

    service sshd restart

To verify that all is ready, ssh into the host as user ``root`` with the password ``mfsroot``. Once that works, log out again and you are ready to continue with :doc:`/setup/bootstrapping`.


Hetzner
-------

The German ISP `Hetzner <http://www.hetzner.de>`_ provides dedicated servers with FreeBSD support. In a nutshell, boot the machine into their so-called *Rescue System* `using their robot <https://robot.your-server.de/server>`_ and choose *FreeBSD* as OS. The machine will boot into a modified version of mfsBSD.

The web UI will then provide you with a one-time root password – make sure it works by SSHing into the host as ``root`` and you are ready for continuing with :doc:`/setup/bootstrapping`.


vmWare
------

Since BSDploy (currently) doesn't support automated provisioning of vmWare instances (like it does for VirtualBox) you will need to manually create a vmWare instance and then follow the steps above for it, except that instead of downloading the image referenced there you need one specifically for booting into a virtual machine, IOW download like so::

    mkdir downloads
    ploy-download http://mfsbsd.vx.sk/files/iso/9/amd64/mfsbsd-se-9.2-RELEASE-amd64.iso 4ef70dfd7b5255e36f2f7e1a5292c7a05019c8ce downloads/

Then create a new virtual machine, set the above image as boot device and continue with :doc:`/setup/bootstrapping`.
