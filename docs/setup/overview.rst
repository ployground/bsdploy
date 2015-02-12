Overview
========

The life cycle of a system managed by BSDploy is divided into three distinct segments:

1. provisioning

2. bootstrapping

3. configuration

Specifically:

- At the end of the provisioning process we have a system that has booted into an installer (usually mfsBSD) which is ready for bootstrapping
- At the end of the bootstrapping process we have installed and booted into a vanilla FreeBSD system with just the essential requirements to complete the actual configuration
- At the end of the configuration process we have a FreeBSD system with a pre-configured ``ezjail`` setup which can be managed by BSDploy.

Conceptually, the provider of a jailhost is a separate entity from the jailhost itself, i.e. in a VirtualBox based setup you could have the following::

	[vb-instance:ploy-demo]
	vm-ostype = FreeBSD_64
	[...]

	[ez-master:jailhost]
	instance = ploy-demo
	[...]

	[ez-instance:webserver]
	master = jailhost
	[...]

Here we define a VirtualBox instance (``vb-instance``) named ``ploy-demo`` and a so-called master named ``jailhost`` which in turn contains a jail instance named ``webserver``.

This approach allows us to hide the specific details of a provider and also to replace it with another one, i.e. :doc:`in a staging scenario </advanced/staging>` where a production provider such as a 'real' server or EC2 instance is replaced with a VirtualBox.

In the following we will document the entire provisioning process for each supported provider separately (eventhough there is a large amount of overlap), so you can simply pick the one that suits your setup and then continue with the configuration step which is then the same for all providers.

In a nutshell, though, given the previous example setup, what you need to do is this::

	ploy start ploy-demo
	ploy bootstrap jailhost
	ploy configure jailhost
	ploy start webserver


Project setup and directory structure
-------------------------------------

``ploy`` and thus by extension also BSDploy have a "project based" approach, meaning that all configuration, playbooks, assets etc. for one given  use case (a.k.a. "project") are contained in a single directory, as opposed to having a central configuration such as ``/usr/local/etc/ploy.conf``.

The minimal structure of such a directory is to contain a subdirectory named ``etc`` in which the main configuration file ``ploy.conf`` is located.

Since BSDploy treats this directory technically as an :ref:`Ansible directory <dir-structure>` you typically would also have additional top-level directories such as ``roles``, ``host_vars`` etc.

Another (entirely optional) convention is to have a top-level directory named ``downloads`` where assets such as installer images or package archives are placed.

This approach was also chosen because most of the times project directories are version controlled and for example ``downloads/`` can then be safely ignored, because all of its contents are a) large, binary files and b) easily replaceable whereas ``etc/`` often contains sensitive, project specific data such as private keys, certificates etc. and may be even part of a different repository altogether.


Next step: Provisioning
-----------------------

Basically, unless you want to use one of the specific provisioners such as EC2 or VirtualBox, just use a plain instance:

.. toctree::
   :maxdepth: 1

   provisioning-plain
   provisioning-virtualbox
   provisioning-ec2
