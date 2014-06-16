Quickstart
==========

This quickstart is intending to provide the shortest possible path from an empty project directory to a running jail inside a provisioned host. 

It takes several shortcuts on its way but it should give you a good idea about how BSDploy works and leave you with a running instance that you can use as a stepping stone for further exploration, i.e. following along the tutorial.

The process consists of:

- booting a host machine into a FreeBSD installer
- then installing FreeBSD onto the host (**bootstrapping**)
- rebooting into the freshly installed FreeBSD
- then **configuring** the vanilla installation to our needs
- and finally creating a 'hello world' jail inside of it.


Using Virtualbox
----------------

To give us the luxury of running against a well-defined context, this quickstart uses `virtualbox <https://www.virtualbox.org>`_, a free, open source PC virtualization. If you don't have it installed on your system, head over to the `downloads section <https://www.virtualbox.org/wiki/Downloads>`_ and install it for your platform. We'll wait! If you can't be bothered, following along anyway should still be useful, though.


Getting the FreeBSD installer
-----------------------------

BSDploy has the notion of an environment, which is just fancy talk for a directory with specific conventions. Let's create one::

	mkdir ploy-quickstart
	cd ploy-quickstart

First, we need to download a FreeBSD boot image. BSDploy uses `mfsBSD <http://mfsbsd.vx.sk>`_ which is basically the official FreeBSD installer plus pre-configured SSH access.

BSDploy provides a small cross-platform helper for downloading assets via HTTP which also checks the integrity of the downloaded file::

	mkdir downloads
	ploy-download http://mfsbsd.vx.sk/files/iso/9/amd64/mfsbsd-se-9.2-RELEASE-amd64.iso 4ef70dfd7b5255e36f2f7e1a5292c7a05019c8ce downloads/


Configuring the virtual instance
--------------------------------

Since BSDploy also handles provisioning, we can configure the virtualbox instance within the main configuration file. It is named ``ploy.conf`` and lives inside a top-level directory named ``etc`` by default::

	mkdir etc

..note: This is directory contains not only your configuration but also all other settings and assets that are specific to *your particular project*, i.e. oftentimes this directory is kept under separate version control, for safe-keeping of certificates, private keys etc.

Inside it create a file named ``ploy.conf`` with the following contents::

	[vb-instance:ploy-demo]
	vm-ostype = FreeBSD_64
	vm-memory = 512
	vm-accelerate3d = off
	vm-acpi = on
	vm-rtcuseutc = on
	vm-boot1 = disk
	vm-boot2 = dvd
	vm-nic1 = hostonly
	vm-hostonlyadapter1 = vboxnet0
	vm-nic2 = nat
	vm-natpf2 = ssh,tcp,,44003,,22
	storage =
	    --type dvddrive --medium ../downloads/mfsbsd-se-9.2-RELEASE-amd64.iso
	    --medium vb-disk:boot

	[vb-disk:boot]
	size = 102400

Now we can start it up::

	ploy start ploy-demo

This should fire up virtualbox and boot a VirtualBOX VM into mfsBSD.


Bootstrapping the host
----------------------

To bootstrap the jailhost, we need to define it first. This is done with an ``ez-master`` entry in ``ploy.conf``. So add this::

	[ez-master:jailhost]
	instance = ploy-demo

This creates an ezjail jailhost (``ez-master``) named ``jailhost`` (doh!) and tells BSDploy that it lives / should live inside the provisioning instance named ``ploy-demo`` (our freshly created virtual machine).

But since none of this has happened yet, we need to tell BSDploy to make it so, like this::

	ploy bootstrap

This will ask you to provide a SSH public key (answer ``y`` if you have one in ``~/.ssh/identity.pub``).

Next it will give you one last chance to abort before it commences to wipe the target drive, so answer ``y`` again.

After the installation has completed, note the final output, as it contains the SSH fingerprint of the newly configured SSH daemon, for example::

	The SSH fingerprint of the newly bootstrapped server is:
	2048 f3:51:c2:2a:94:c3:06:0e:02:e0:87:51:73:f0:dc:6f  root@mfsbsd (RSA)

Before we can continue you need to add that fingerprint to the jailhost configuration, as BSDploy refuses to connect to hosts it doesn't know its fingerprint (we find that a reasonable behavior), i.e. add the following line to ``ploy.conf`` so that your jailhost definition looks like so::

	[ez-master:jailhost]
	instance = ploy-demo
	fingerprint = f3:51:c2:2a:94:c3:06:0e:02:e0:87:51:73:f0:dc:6f

To make sure that everything has worked so far, let's take a look at the host by logging into it via SSH. ``bsdploy`` provides a command for that, too::

	ploy ssh jailhost
	FreeBSD 9.2-RELEASE (GENERIC) #6 r255896M: Wed Oct  9 01:45:07 CEST 2013
	[...]

Let's take a quick look::

	root@jailhost:~ # pkg info
	gettext-0.18.3.1_1             GNU gettext package
	libiconv-1.14_3                Character set conversion library
	python27-2.7.6_4               Interpreted object-oriented programming language
	root@jailhost:~ # zpool list
	NAME     SIZE  ALLOC   FREE    CAP  DEDUP  HEALTH  ALTROOT
	system  19.9G   584M  19.3G     2%  1.00x  ONLINE  -
	root@jailhost:~ # zfs list
	NAME              USED  AVAIL  REFER  MOUNTPOINT
	system            584M  19.0G    31K  none
	system/root       583M  19.0G   533M  /
	system/root/tmp    37K  19.0G    37K  /tmp
	system/root/var  50.6M  19.0G  50.6M  /var

A few things to note:

- ``pkg`` is installed and configured
- ``python`` has been installed
- there is one zpool which contains the system
- not much else

In other words, there's still work to do, so let's log out and continue...


Configuring the host
--------------------

Now we can configure the vanilla installation. This step is performed internally using `ansible playbooks <http://docs.ansible.com/playbooks_intro.html>`_, which are divided into different so-called *roles*. For the tutorial we will need the DHCP role (since virtualbox provides DHCP to the VM), the main jailhost role and in addition we want to show off BSDploy's default ZFS layout, so add the following lines to the jailhost configuration to make it look like so::

	[ez-master:jailhost]
	instance = ploy-demo
	fingerprint = xxxx
	roles =
	    dhcp_host
	    jails_host
	    data_zfs_layout

With this information, BSDploy can set to work::

	ploy configure ploy-demo

Let's log in once more and take another look::

	ploy ssh jailhost
	[...]

Package-wise nothing much has changed – only ``ezjail`` has been installed. BSDploy tries hard, to keep the jailhost clean::

	root@jailhost:~ # pkg info
	ezjail-3.4.1                   Framework to easily create, manipulate, and run FreeBSD jails
	gettext-0.18.3.1_1             GNU gettext package
	libiconv-1.14_3                Character set conversion library
	python27-2.7.6_4               Interpreted object-oriented programming language

There is now a second zpool called ``tank`` and ``ezjail`` has been configured to use it::

	root@jailhost:~ # zpool list
	NAME     SIZE  ALLOC   FREE    CAP  DEDUP  HEALTH  ALTROOT
	system  19.9G   584M  19.3G     2%  1.00x  ONLINE  -
	tank    78.5G   389M  78.1G     0%  1.00x  ONLINE  -
	root@jailhost:~ # zfs list
	NAME                  USED  AVAIL  REFER  MOUNTPOINT
	system                584M  19.0G    31K  none
	system/root           584M  19.0G   533M  /
	system/root/tmp        38K  19.0G    38K  /tmp
	system/root/var      50.7M  19.0G  50.7M  /var
	tank                  389M  76.9G   144K  none
	tank/jails            389M  76.9G  8.05M  /usr/jails
	tank/jails/basejail   377M  76.9G   377M  /usr/jails/basejail
	tank/jails/newjail   3.58M  76.9G  3.58M  /usr/jails/newjail

But there aren't any jails configured yet::

	root@jailhost:~ # ezjail-admin list
	STA JID  IP              Hostname                       Root Directory
	--- ---- --------------- ------------------------------ ------------------------

Let's change that...


Configuring a jail
------------------

Add the following lines to ``etc/ploy.conf``::


	[ez-instance:demo_jail]
	ip = 10.0.0.1

and start the jail like so::

	ploy start demo_jail

Let's check on it first, by logging into the host::

	ploy ssh jailhost
	root@jailhost:~ # ezjail-admin list
	STA JID  IP              Hostname                       Root Directory
	--- ---- --------------- ------------------------------ ------------------------
	ZR  1    10.0.0.1        demo_jail                      /usr/jails/demo_jail

Ok, we have a running jail, listening on a private IP – how do we communicate with it? Basically, there are two options (besides giving it a public IP): either port forwarding from the host or using a SSH proxy command. For the tutorial we will chose the latter. Log out from the jailhost and add the following lines to ``ploy.conf`` so that the jail definition looks like this::

	[ez-instance:demo_jail]
	ip = 10.0.0.1
	proxycommand = nohup ploy-ssh jailhost -W {ip}:22
	proxyhost = jailhost

Now you can log into the jail via ``ploy``, just like with the host::

	ploy ssh demo_jail
