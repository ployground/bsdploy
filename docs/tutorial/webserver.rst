Webserver
---------

The idea is that the webserver lives in its own jail and receives all HTTP traffic and then redirects the requests as required to the individual jails.

The webserver jail itself will host a simple website that lists and links the available services.

The website itself will reside in a dedicated ZFS that will be mounted into the jail, so let's start with creating this.

In ``etc/ploy.conf`` from the quickstart you should have the following ezjail master::

	[ez-master:jailhost]
	instance = ploy-demo
	roles =
	    dhcp_host
	    jails_host

To set up the ZFS layout we will replace the inline roles with a dedicated playbook, so let's delete the ``roles =`` entry and create a top-level file names ``jailhost.yml`` with the following contents::

	---
	- hosts: jailhost
	  user: root
	  roles:
	    - { role: dhcp_host }
	    - { role: jails_host, tags: ['jails_host'] }
	  tasks:
	    - name: ensure ZFS file systems are in place
	      zfs: name={{ item }} state=present
	      with_items:
	      - tank/htdocs
	      tags: zfs-layout

.. note:: Here we also demonstrate how to tie roles to tags for the ``jails_host`` role, by using YAML dictionaries as list items

Now we can create the webserver host and mount the website ZFS into it like so::

	[ez-instance:webserver]
	master = jailhost
	ip = 10.0.0.2
	roles =
		webserver
	mounts =
	    src=tank/htdocs dst=/usr/local/www/data
