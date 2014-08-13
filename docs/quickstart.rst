Quickstart
==========

This quickstart provides the shortest possible path from an empty project directory to a running jail inside a provisioned host.

It is designed to be followed along, with all required commands and configuration provided in a copy & paste friendly format.

It takes several shortcuts on its way but it should give you a good idea about how BSDploy works and leave you with a running instance that you can use as a stepping stone for further exploration.

The process consists of:

- creating a VirtualBox based host (**provisioning**)
- then installing FreeBSD onto it (**bootstrapping**)
- then **configuring** the vanilla installation to our needs
- and finally creating a 'hello world' jail inside of it.

.. note:: Before you begin with this tutorial, make sure you have :doc:`installed bsdploy </installation>`.

Using VirtualBox
----------------

To give us the luxury of running against a well-defined context, this quickstart uses `VirtualBox <https://www.virtualbox.org>`_, a free, open source PC virtualization platform. If you don't have it installed on your system, head over to their `downloads section <https://www.virtualbox.org/wiki/Downloads>`_ and install it for your platform. We'll wait! If you can't be bothered, following along anyway should still be useful, though.

Since VirtualBox support is optional and BSDploy is fairly modular, you will need to install ``ploy_virtualbox`` to follow this quickstart like so::

	% pip install --pre ploy_virtualbox


Getting the FreeBSD installer
-----------------------------

BSDploy has the notion of an environment, which is just fancy talk for a directory with specific conventions. Let's create one::

	% mkdir ploy-quickstart
	% cd ploy-quickstart

First, we need to download a FreeBSD boot image. BSDploy uses `mfsBSD <http://mfsbsd.vx.sk>`_ which is basically the official FreeBSD installer plus pre-configured SSH access.

BSDploy provides a small cross-platform helper for downloading assets via HTTP which also checks the integrity of the downloaded file::

	% mkdir downloads
	% ploy-download http://mfsbsd.vx.sk/files/iso/10/amd64/mfsbsd-se-10.0-RELEASE-amd64.iso 06165ce1e06ff8e4819e86c9e23e7d149f820bb4 downloads/


Configuring the virtual machine
-------------------------------

Since BSDploy also handles provisioning, we can configure the virtualbox instance within the main configuration file. It is named ``ploy.conf`` and lives inside a top-level directory named ``etc`` by default::

	% mkdir etc

Inside it create a file named ``ploy.conf`` with the following contents::

	[vb-hostonlyif:vboxnet0]
	ip = 192.168.56.1

	[vb-dhcpserver:vboxnet0]
	ip = 192.168.56.2
	netmask = 255.255.255.0
	lowerip = 192.168.56.100
	upperip = 192.168.56.254

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
	    --type dvddrive --medium ../downloads/mfsbsd-se-10.0-RELEASE-amd64.iso
	    --medium vb-disk:boot

	[vb-disk:boot]
	size = 102400

Now we can start it up::

	% ploy start ploy-demo

This should fire up virtualbox and boot a VirtualBox VM into mfsBSD.


Bootstrapping the host
----------------------

To bootstrap the jailhost, we need to define it first. This is done with an ``ez-master`` entry in ``ploy.conf``. So add this::

	[ez-master:jailhost]
	instance = ploy-demo

This creates an ezjail jailhost (``ez-master``) named ``jailhost`` and tells BSDploy that it lives / should live inside the provisioning instance named ``ploy-demo`` (our freshly created virtual machine).

But since none of this has happened yet, we need to tell BSDploy to make it so, like this::

	% ploy bootstrap

This will ask you to provide a SSH public key (answer ``y`` if you have one in ``~/.ssh/identity.pub``).

Next it will give you one last chance to abort before it commences to wipe the target drive, so answer ``y`` again.

To make sure that everything has worked so far, let's take a look at the host by logging into it via SSH. ``bsdploy`` provides a command for that, too::

	% ploy ssh jailhost
	FreeBSD 9.2-RELEASE (GENERIC) #6 r255896M: Wed Oct  9 01:45:07 CEST 2013
	[...]

Let's take a quick look around::

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

Now we can configure the vanilla installation. This step is performed internally using `ansible playbooks <http://docs.ansible.com/playbooks_intro.html>`_, which are divided into different so-called *roles*. For the tutorial we will need the DHCP role (since Virtualbox provides DHCP to the VM) and the main jailhost role so add the following lines to the jailhost configuration in ``ploy.conf`` to make it look like so::

	[ez-master:jailhost]
	instance = ploy-demo
	roles =
	    dhcp_host
	    jails_host

With this information, BSDploy can get to work::

	% ploy configure jailhost

Let's log in once more and take another look::

	% ploy ssh jailhost
	[...]

Package-wise nothing much has changed – only ``ezjail`` has been installed::

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


Creating a jail
---------------

Add the following lines to ``etc/ploy.conf``::


	[ez-instance:demo_jail]
	ip = 10.0.0.1

and start the jail like so::

	% ploy start demo_jail

Let's check on it first, by logging into the host::

	ploy ssh jailhost
	root@jailhost:~ # ezjail-admin list
	STA JID  IP              Hostname                       Root Directory
	--- ---- --------------- ------------------------------ ------------------------
	ZR  1    10.0.0.1        demo_jail                      /usr/jails/demo_jail

Ok, we have a running jail, listening on a private IP – how do we communicate with it?
Basically, there are two options (besides giving it a public IP): either port forwarding from the host or using a SSH proxy command.

Rather conveniently `ploy_ezjail <https://github.com/ployground/ploy_ezjail>`_ has defaults for the latter.

Log out from the jailhost and run this::

	# ploy ssh demo_jail
	FreeBSD 9.2-RELEASE (GENERIC) #6 r255896M: Wed Oct  9 01:45:07 CEST 2013

	Gehe nicht über Los.
	root@demo_jail:~ #

and there you are, inside the jail.

But frankly, that's not very interesting. As a final step of this introduction, let's configure it to act as a simple webserver using an ansible playbook.


Configuring a jail
------------------

Like with the jailhost, we could assign roles to our demo jail, but another way is to create a playbook with the same name. If such a playbook exists, BSDploy will use that when you call ``configure``. So, create a top-level file named ``jailhost-demo_jail.yml`` with the following content:

.. code-block:: yaml

	---
	- hosts: jailhost-demo_jail
	  tasks:
	    - name: install nginx
	      pkgng: name=nginx state=present
	    - name: enable nginx at startup time
	      lineinfile: dest=/etc/rc.conf regexp=^nginx_enable= line=nginx_enable=\"YES\"
	    - name: make sure nginx is running or reloaded
	      service: name=nginx state=restarted

and apply it::

	% ploy configure demo_jail

Ok, now we have a jail with a webserver running inside of it. How do we access it? Right, *port forwarding*...


Port forwarding
***************

Port forwarding from the host to jails is implemented using ``ipnat`` and BSDploy offers explicit support for configuring it.

To do so, make a folder named ``host_vars``::

	% mkdir host_vars

and create the file ``jailhost.yml`` in it with the following content::

	ipnat_rules:
	    - "rdr em0 {{ ansible_em0.ipv4[0].address }}/32 port 80 -> {{ hostvars['jailhost-demo_jail']['ploy_ip'] }} port 80"

To activate the rules, re-apply the jail host configuration.
Ansible will figure out, that it needs to update them (and only them) and then restart the network. However, in practice running the entire configuration can take quite some time, so if you already know you only want to update some specific sub set of tasks you can pass in one or more tags. In this case for updating the ipnat rules::

	% ploy configure jailhost -t ipnat_rules

Since the demo is running inside a host that got its IP address via DHCP we will need to find that out before we can access it in the browser.

To find out, which one was assigned run ``ifconfig`` like so::

	% ploy ssh jailhost 'ifconfig em0'
	em0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
		options=9b<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,VLAN_HWCSUM>
		ether 08:00:27:87:2e:40
		inet 192.168.56.108 netmask 0xffffff00 broadcast 192.168.56.255
		nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
		media: Ethernet autoselect (1000baseT <full-duplex>)
		status: active

Visit the IP in your browser and you should be greeted with the default page of ``nginx``.
