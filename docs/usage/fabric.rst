Fabric integration
==================

.. epigraph::

	`Fabric <http://www.fabfile.org>`_ is a Python library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks.

BSDploy support applying of Fabric scripts to jails and jail hosts via the `ploy_fabric <http://ploy.readthedocs.org/en/latest/ploy_fabric.html>`_ plugin.

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

You can then execute an task defined in that file by calling ``do``, i.e.::

	# ploy do webserver restart_httpd
	[root@jailhost-webserver] run: service nginx restart
	[root@jailhost-webserver] out: Performing sanity check on nginx configuration:
	[root@jailhost-webserver] out: nginx: the configuration file /usr/local/etc/nginx/nginx.conf syntax is ok
	[root@jailhost-webserver] out: nginx: configuration file /usr/local/etc/nginx/nginx.conf test is successful
	[root@jailhost-webserver] out: Stopping nginx.
	[root@jailhost-webserver] out: Waiting for PIDS: 5847.
	[root@jailhost-webserver] out: Performing sanity check on nginx configuration:
	[root@jailhost-webserver] out: nginx: the configuration file /usr/local/etc/nginx/nginx.conf syntax is ok
	[root@jailhost-webserver] out: nginx: configuration file /usr/local/etc/nginx/nginx.conf test is successful
	[root@jailhost-webserver] out: Starting nginx.
	[root@jailhost-webserver] out: 

You can also list all available tasks with the ``-l`` parameter::

	ploy do webserver -l
	Available commands:

	    info
	    restart_httpd

