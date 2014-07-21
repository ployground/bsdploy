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


Use defaults
------------

Currently the webserver serves the default site located at ``/usr/local/www/nginx`` which is a symbolic link to ``nginx-dist``.

Now, to switch it the website located inside the ZFS filesystem we could either change the nginx configuration to point to it but in practice it can be a good idea to use default settings as much as possible and instead make the environment match the default.
*Every custom configuration file you can avoid is a potential win*.

In this particular case, let's mount the website into the default location. First we need to remove the symbolic link that has been created by the nginx start up.
Since this is truly a one-time operation (if we re-run the modified playbook against a fresh instance the symbolic link would not be created and wouldn't need to be removed) we can use ploy's ability to execute ssh commands like so::

	ploy ssh jailhost "rm /usr/jails/webserver/usr/local/www/nginx"

Now we can change the mountpoint in ``ploy.conf``::

	[ez-instance:webserver]
	master = jailhost
	ip = 10.0.0.2
	mounts =
	    src=tank/htdocs dst=/usr/local/www/nginx ro=true

Unfortunately, currently the only way to re-mount is to stop and start the jail in question, so let's do that::

	ploy stop webserver
	ploy start webserver

Reload the website in your browser: you should now receive a ``Forbidden``.
Let's change that!


Fabric integration
------------------

So far we've used ansible to configure the host and the jail.
Its declarative approach is perfect for this.
But what about maintenance tasks such as updating the contents of a website?
Such tasks are a more natural fit for an *imperative* approach and ``ploy_fabric`` gives us a neat way of doing this.

Let's create a top-level file named ``fabfile.py`` with the following contents::

	from fabric import api as fab

	def upload_website():
		ansible_vars = fab.env.instance.get_ansible_variables()
		fab.put('htdocs/*', '/usr/jails/webserver/usr/local/www/nginx/')

Since the webserver jail only has read-access, we need to upload the website via the host (for now), so let's associate the fabric file with the host by making its entry in ``ploy.conf`` look like so::

	[ez-master:jailhost]
	instance = ploy-demo
	fabfile = ../fabweb.py

Create a simple index page::

	mkdir htdocs
	echo "Hello Berlin" >> htdocs/index.html

Then upload it::

	ploy do jailhost upload_website

and reload the website.


Exercise
--------

Requiring write-access to the jail host in order to update the website is surely not very clever.

Your task is to create a jail named ``website-edit`` that contains a writeable mount of the website and which uses a modified version of the fabric script from above to update the contents.

Bonus: put the path to the website on the host into a ansible variable defined in ploy.conf and make the fabric script reference it.
