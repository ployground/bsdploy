Fabric integration
==================

.. epigraph::

	`Fabric <http://www.fabfile.org>`_ is a Python library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks.

BSDploy supports applying Fabric scripts to jails and jail hosts via the `ploy_fabric <http://ploy.readthedocs.org/en/latest/ploy_fabric.html>`_ plugin.

Before you can run a fabric script against a target it must have a fabric file assigned to it in ``ploy.conf``, i.e.::

	[instance:webserver]
	...
	fabfile = ../fabfile.py

Given the following contents of ``fabfile.py``::

	from fabric import api as fab

	fab.env.shell = '/bin/sh -c'

	@fab.task
	def info():
		fab.run('uname -a')


	@fab.task
	def restart_httpd():
		fab.run('service nginx restart')

You can then execute a task defined in that file by calling ``do``, i.e.::

	# ploy do webserver info
	[root@jailhost-webserver] run: uname -a
	[root@jailhost-webserver] out: FreeBSD webserver 9.2-RELEASE FreeBSD 9.2-RELEASE #6 r255896M: Wed Oct  9 01:45:07 CEST 2013     root@mfsbsd:/usr/obj/usr/src/sys/GENERIC  amd64
	[root@jailhost-webserver] out: 

You can also list all available tasks with the ``-l`` parameter::

	ploy do webserver -l
	Available commands:

	    info
	    restart_httpd

