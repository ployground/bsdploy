Webserver
=========

The idea is that the webserver lives in its own jail and receives all HTTP traffic and then redirects the requests as required to the individual jails.

The webserver jail itself will host a simple website that lists and links the available services.

The website itself will in a dedicated ZFS that will be mounted into the jail, so let's start with creating this.

In ``etc/ploy.conf`` from the quickstart you should have the following ezjail master::

	[ez-master:jailhost]
	instance = ploy-demo
	roles =
	    dhcp_host
	    jails_host


ZFS mounting
------------

To set up the ZFS layout we will replace the inline roles with a dedicated playbook, so let's delete the ``roles =`` entry and create a top-level file names ``jailhost.yml`` with the following contents::

	---
	- hosts: jailhost
	  user: root
	  roles:
	    - { role: dhcp_host }
	    - { role: jails_host, tags: ['jails_host'] }

.. note:: Here we also demonstrate how to tie roles to tags for the ``jails_host`` role, by using YAML dictionaries as list items

Once we have a playbook in place, it becomes easy to add custom tasks::

	  tasks:
	    - name: ensure ZFS file systems are in place
	      zfs: name={{ item }} state=present
	      with_items:
	      - tank/htdocs
	      tags: zfs-layout

To apply the playbook it's easiest to call the ``configure`` command again.
While Ansible is smart enough to only apply those parts that actually need to be applied again that process can become quite slow, as playbooks grow in size.
So here, we tag the new task with ``zfs-layout``, so we can call it explicitly::

	ploy configure jailhost -t zfs-layout

.. note:: You should see an ``INFO`` entry in the output that tells you which playbook the ``configure`` command has used.

Now we can create the webserver host and mount the website ZFS into it like so::

	[ez-instance:webserver]
	master = jailhost
	ip = 10.0.0.2
	mounts =
	    src=tank/htdocs dst=/usr/local/www/data ro=true

.. note:: Mounting filesystems into jails gives us the ability to mount them read-only, like we do in this case.

Let's start the new jail::

	ploy start webserver


Instance playbooks
------------------

Note that the webserver jail doesn't have a role assigned.
Roles are useful for more complex scenarios that are being re-used.
For smaller tasks it's often easier to simply create a one-off playbook for a particular host.

To associate a playbook with an instance you need to create a top-level YAML file with the same name as the instance – like we did above for the jailhost.
For jail instances, this name contains both the name of the master instance *and* the name of the jail, so let's create a top-level file named ``jailhost-webserver`` with the following contents::

	---
	- hosts: jailhost-webserver
	  tasks:
	    - name: install nginx
	      pkgng: name=nginx state=present
	    - name: enable nginx at startup time
	      lineinfile: dest=/etc/rc.conf state=present line='nginx_enable=YES' create=yes
	    - name: make sure nginx is running or reloaded
	      service: name=nginx state=restarted

In the above playbook we demonstrate

- how to install a package with the ``pkgng`` module from ansible
- enable a service in ``rc.conf`` using the ``lineinfile`` comannd
- ensure a service is running with the ``service`` command

Let's give that a spin::

	ploy configure webserver

.. note:: If the name of a jail is only used in a single master instance, ``ploy`` allows us to address it without stating the full name for convenience. IOW the above command is an alias to ``ploy configure jailhost-webserver``.


"Publishing" jails
------------------

Eventhough the webserver is now running, we cannot reach it from the outside, we first need to explicitly enable access. While there are several possibilites to achieve this, we will use ``ipnat``, just like in the quickstart.

So, create or edit ``host_vars/jailhost.yml`` to look like so::

	ipnat_rules:
	    - "rdr em0 {{ ansible_em0.ipv4[0].address }}/32 port 80 -> {{ hostvars['jailhost-webserver']['ploy_ip'] }} port 80"

To activate the rules, re-apply the jail host configuration::

	ploy configure jailhost -t ipnat_rules

You should now be able to access the default nginx website at the ``http://192.168.56.100`` address.
