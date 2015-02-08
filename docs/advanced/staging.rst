Staging
=======

One use case that BSDploy was developed for is to manage virtual copies of production servers.

The idea is to have a safe environment that mirrors the production environment as closely as possible into which new versions of applications or system packages can be installed or database migrations be tested etc.

But safe testing and experimenting is just one benefit, the real benefit comes into play, once you've tweaked your staging environment to your liking. Since BSDploy makes it easy for you to capture those changes and tweaks into playbooks and fabric scripts, applying them to production is now just a matter changing the target of a ``ploy`` command.


Extended configuration files
****************************

To help you keep the staging and production environment as similar as possible we will use the ability of ``ploy`` to inherit configuration files.

We define the general environment (one or more jail hosts and jails) in a ``base.conf`` and create two 'top-level' configuration files ``staging.conf`` and ``production.conf`` which each extend ``base.conf``.

During deployment we specify the top-level configuration file via' ``ploy -c xxx.conf``. A variation of this is to name the staging configuration file ``ploy.conf`` which then acts as default. This has the advantage that during development of the environment you needn't bother with explicitly providing a configuration file and that when moving to production you need to make the extra, explicit step of (now) providing a configuration file, thus minimizing the danger of accidentally deploying something onto production.

Here is an example ``base.conf``::

	[ez-master:jailhost]
	instance = provisioner
	roles = jails_host

	[instance:webserver]
	master = jailhost
	ip = 10.0.0.1


	[instance:appserver]
	master = jailhost
	ip = 10.0.0.2

and ``staging.conf``::

	[global]
	extends = base.conf

	[vb-instance:provisioner]
	vm-ostype = FreeBSD_64
	[...]

and ``production.conf``::

	[global]
	extends = base.conf

	[ec2-instance:provisioning]
	ip = xxx.xxx.xxx.xxx
	instance_type = m1.small
	# FreeBSD 9.2-RELEASE instance-store eu-west-1 from daemonology.net/freebsd-on-ec2/
	image = ami-3e1ef949
	[...]

.. note:: In practice, it can often be useful to split this out even further. We have made good experiences with using a virtualbox based setup for testing the deployment during its development, then once that's finished we apply it to a public server (that can be accessed by stakeholders of the project for evaluation) that actually runs on the same platform as the production machine and once that has been approved we finally apply it to the production environment. YMMV.


Staging with FQDN
*****************

A special consideration when deploying web applications is how to test the entire stack, including the webserver with fully qualified domain names and SSL certificates etc.

BSDploy offers a neat solution using the following three components:

- template based webserver configuration
- `xip.io <http://xip.io>`_ based URLs for testing
- VirtualBox `host-only networking <http://www.virtualbox.org/manual/ch06.html#network_hostonly>`_

IOW if you're deploying a fancy-pants web application at your production site ``fancypants.com`` using i.e. a nginx configuration snippet like such::

	server {
	    server_name  fancypants.com;
		[...]
	}

Change it to this::

	server {
	    server_name  fancypants.com{{fqdn_suffix}};
		[...]
	}

And in your ``staging.conf`` you define ``fqdn_suffix`` to be i.e. ``.192.168.56.10.xip.io`` and in ``production.conf`` to an empty string.

Finally, configure the VirtualBox instance in staging to use a second nic (in addition to the default host-only interface) via DHCP so it can access the internet::

	[vb-instance:provisioner]
	vm-nic2 = nat

``ploy_virtualbox`` will ensure that the virtual network ``vboxnet0`` exists (if it doesn't already).
You can then use the fact that VirtualBox will set up a local network (default is ``192.168.56.xxx``) with a DHCP range from ``.100 - .200`` and assign your nic1 (``em0`` in our case) a static IP of, i.e. ``192.168.56.10`` which you then can use in the abovementioned xip.io domain name.

The net result? Deploy to staging and test your web application's full stack (including https, rewriting etc.) in any browser under ``https://fancypants.com.192.168.56.10.xip.io`` in the knowledge that the only difference between that setup and your (eventual) production environment is a single suffix string.
