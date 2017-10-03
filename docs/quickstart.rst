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

    % pip install ploy_virtualbox


Initializing the project environment
------------------------------------

BSDploy has the notion of an environment, which is just fancy talk for a directory with specific conventions. Let's create one::

    % mkdir ploy-quickstart
    % cd ploy-quickstart


Configuring the virtual machine
-------------------------------

The main configuration file is named ``ploy.conf`` and lives inside a top-level directory named ``etc`` by default::

    % mkdir etc

Inside it create a file named ``ploy.conf`` with the following contents::

    [vb-instance:ploy-demo]
    vm-nic2 = nat
    vm-natpf2 = ssh,tcp,,44003,,22
    storage =
        --medium vb-disk:defaultdisk
        --type dvddrive --medium http://mfsbsd.vx.sk/files/iso/10/amd64/mfsbsd-se-10.3-RELEASE-amd64.iso --medium_sha1 564758b0dfebcabfa407491c9b7c4b6a09d9603e


This creates a VirtualBox instance named ``ploy-demo``. By default BSDploy provides it with a so-called "host only interface" but since that cannot be used to connect to the internet we explicitly configure a second one using NAT (mfsBSD will configure it via DHCP) and in addtion we create a port forwarding from ``localhost`` port ``44003`` to port ``22`` on the box - in essence allowing us to SSH into it via localhost.

Next, we assign a virtual disk named ``defaultdisk`` onto which we will install the OS. This special disk is created automatically by BSDploy if it doesn't exist yet (it's sparse by default, so it won't take up much space on your disk).

Finally, we configure a virtual optical drive to boot from the official mfsBSD 'special edition' installation image. By providing a download URL and checksum, BSDploy will automatically download it for us.

Now we can start it up::

    % ploy start ploy-demo

This should download the mfsBSD image, fire up VirtualBox and boot our VM into mfsBSD.


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
    FreeBSD 10.3-RELEASE (GENERIC) #0 r297264: Fri Mar 25 02:10:02 UTC 2016

    Welcome to FreeBSD!
    [...]

Let's take a quick look around. First, what packages have been installed?::

    root@jailhost:~ # pkg info
    gettext-runtime-0.19.3         GNU gettext runtime libraries and programs
    indexinfo-0.2.2                Utility to regenerate the GNU info page index
    libffi-3.0.13_3                Foreign Function Interface
    pkg-1.4.3                      Package manager
    python27-2.7.9                 Interpreted object-oriented programming language

Next, what's the ZFS scenario?::

    root@jailhost:~ # zpool list
    NAME     SIZE  ALLOC   FREE   FRAG  EXPANDSZ    CAP  DEDUP  HEALTH  ALTROOT
    system  19.9G   931M  19.0G     2%         -     4%  1.00x  ONLINE  -
    root@jailhost:~ # zfs list
    NAME              USED  AVAIL  REFER  MOUNTPOINT
    system            931M  18.3G    19K  none
    system/root       931M  18.3G   876M  /
    system/root/tmp    21K  18.3G    21K  /tmp
    system/root/var  54.2M  18.3G  54.2M  /var
    root@jailhost:~ # 

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
    gettext-runtime-0.19.3         GNU gettext runtime libraries and programs
    indexinfo-0.2.2                Utility to regenerate the GNU info page index
    libffi-3.0.13_3                Foreign Function Interface
    pkg-1.4.3                      Package manager
    python27-2.7.9                 Interpreted object-oriented programming language
    root@jailhost:~ # 

There is now a second zpool called ``tank`` and ``ezjail`` has been configured to use it::

    root@jailhost:~ # zpool list
    NAME     SIZE  ALLOC   FREE   FRAG  EXPANDSZ    CAP  DEDUP  HEALTH  ALTROOT
    system  19.9G   934M  19.0G     2%         -     4%  1.00x  ONLINE  -
    tank    75.5G   444M  75.1G      -         -     0%  1.00x  ONLINE  -
    root@jailhost:~ # zfs list
    NAME                  USED  AVAIL  REFER  MOUNTPOINT
    system                933M  18.3G    19K  none
    system/root           933M  18.3G   877M  /
    system/root/tmp        21K  18.3G    21K  /tmp
    system/root/var      56.6M  18.3G  56.6M  /var
    tank                  443M  72.7G   144K  none
    tank/jails            443M  72.7G  10.1M  /usr/jails
    tank/jails/basejail   426M  72.7G   426M  /usr/jails/basejail
    tank/jails/newjail   6.37M  72.7G  6.37M  /usr/jails/newjail
    root@jailhost:~ # 


But there aren't any jails configured yet::

    root@jailhost:~ # ezjail-admin list
    STA JID  IP              Hostname                       Root Directory
    --- ---- --------------- ------------------------------ ------------------------
    root@jailhost:~ # 

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
    FreeBSD 10.3-RELEASE (GENERIC) #0 r297264: Fri Mar 25 02:10:02 UTC 2016

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
        - name: Setup nginx to start immediately and on boot
          service: name=nginx enabled=yes state=started

and apply it::

    % ploy configure demo_jail

Ok, now we have a jail with a webserver running inside of it. How do we access it? Right, *port forwarding*...


Port forwarding
***************

Port forwarding from the host to jails is implemented using ``ipnat`` and BSDploy offers explicit support for configuring it.

To do so, make a folder named ``host_vars``::

    % mkdir host_vars

and create the file ``jailhost.yml`` in it with the following content::

    pf_nat_rules:
        - "rdr on em0 proto tcp from any to em0 port 80 -> {{ hostvars['jailhost-demo_jail']['ploy_ip'] }} port 80"

To activate the rules, re-apply the jail host configuration with just the ``pf-conf`` tag.
Ansible will figure out, that it needs to update them (and only them) and then restart the network. However, in practice running the entire configuration can take quite some time, so if you already know you only want to update some specific sub set of tasks you can pass in one or more tags. In this case for updating the ipnat rules::

    % ploy configure jailhost -t pf-conf

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
