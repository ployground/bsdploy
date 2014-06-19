Provisioning
============

The life cycle of a system managed by BSDploy is divided into three distinct segments::

	provisioning -> bootstrapping -> configuration

At the end of this process we have a FreeBSD system with a pre-configured ``ezjail`` setup.

Conceptually, the provider of a jailhost is a separate entity from the jailhost, i.e. in VirtualBox based setup you could have the following::

	[vb-instance:provisioner]
	vm-ostype = FreeBSD_64
	[...]

	[master:jailhost]
	instance = provisioner
	[...]

	[instance:webserver]
	master = jailhost
	[...]

Here we define a VirtualBox instance named ``provisioner`` and a so- called master named ``jailhost`` which in turn conains a jail.

This approach allows us to hide the specific details of a provider and also to replace it with another one, i.e. :doc:`in a staging scenario </narr/staging>` where a production provider such as a 'real' server or EC2 instance is replaced with a VirtualBox.

In the following we will document the entire provisioning process for each supported provider separately (eventhough there is a large amount of overlap), so you can simply pick the one that suits your setup and then continue with the configuration step which is then the same for all providers.
