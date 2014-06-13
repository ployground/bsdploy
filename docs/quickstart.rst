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


Virtualbox
----------

To give us the luxury of running against a well-defined context, this quickstart uses `virtualbox <https://www.virtualbox.org>`_, a free, open source PC virtualization. If you don't have it installed on your system, head over to the `downloads section <https://www.virtualbox.org/wiki/Downloads>`_ and install it for your platform. We'll wait! If you can't be bothered, following along anyway should still be useful, though.


Get assets
----------

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


Bootstrapping
-------------

To bootstrap the jailhost, we need to define it first. This is done with an ``ez-master`` entry in ``ploy.conf``. So add this::

	[ez-master:jailhost]
	instance = ploy-demo

Now we can tell BSDploy to bootstrap the virtualbox VM as a jailhost::

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


Host Configuration
------------------

Now we can configure the vanilla installation. This step is performed internally using ansible playbooks, which are divided into different socalled *roles*. For the tutorial we will need the DHCP role (since virtualbox provides DHCP to the VM), the main jailhost role and in addition we want to show off BSDploy's default ZFS layout, so add the following lines to the jailhost configuration to make it look like so::

	[ez-master:jailhost]
	instance = ploy-demo
	fingerprint = xxxx
	roles =
	    dhcp_host
	    jails_host
	    data_zfs_layout

Currently, ``mr.awsome.ansible`` *requires* us to provide a path to our own playbooks, even, if we don't have any yet, so for now, we need to add the following lines to ``ploy.conf``, as well::

	[ansible]
	playbooks-directory = ..


With this information, BSDploy can set to work::

	ploy configure ploy-demo
