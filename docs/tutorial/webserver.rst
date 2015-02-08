Webserver
=========

The idea is that the webserver lives in its own jail and receives all HTTP traffic and then redirects the requests as required to the individual jails.

The webserver jail itself will host a simple website that lists and links the available services.

The website will be in a dedicated ZFS that will be mounted into the jail, so let's start with creating this.

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
	    - dhcp_host
	    - jails_host

Once we have a playbook in place, it becomes easy to add custom tasks::

	  tasks:
	    - name: ensure ZFS file systems are in place
	      zfs: name={{ item }} state=present mountpoint=/{{ item }}
	      with_items:
	      - tank/htdocs
	      tags: zfs-layout

To apply the playbook it's easiest to call the ``configure`` command again.
While Ansible is smart enough to only apply those parts that actually need to be applied again that process can become quite slow, as playbooks grow in size.
So here, we tag the new task with ``zfs-layout``, so we can call it explicitly::

	ploy configure jailhost -t zfs-layout

.. note:: You should see an ``INFO`` entry in the output that tells you which playbook the ``configure`` command has used.


Exercise
--------

In the quickstart, we've created a demo jail which conveniently already contains a webserver.

Repurpose it to create a jail named ``webserver`` which has nginx installed into it.

Do this by first terminating the demo jail, *then* renaming it, otherwise we will have an 'orphaned' instance which would interfere with the new jail::

	ploy terminate demo_jail

Now we can mount the website ZFS into it like so::

	[ez-instance:webserver]
	master = jailhost
	ip = 10.0.0.2
	mounts =
	    src=/tank/htdocs dst=/usr/local/www/data ro=true

.. note:: Mounting filesystems into jails gives us the ability to mount them read-only, like we do in this case.

Let's start the new jail::

	ploy start webserver


Instance playbooks
------------------

Note that the webserver jail doesn't have a role assigned.
Roles are useful for more complex scenarios that are being re-used.
For smaller tasks it's often easier to simply create a one-off playbook for a particular host.

To associate a playbook with an instance you need to create a top-level YAML file with the same name as the instance – like we did above for the jailhost.
For jail instances, this name contains both the name of the master instance *and* the name of the jail, so let's create a top-level file named ``jailhost-webserver.yml`` with the following contents::

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
- enable a service in ``rc.conf`` using the ``lineinfile`` command
- ensure a service is running with the ``service`` command

Let's give that a spin::

	ploy configure webserver

.. note:: If the name of a jail is only used in a single master instance, ``ploy`` allows us to address it without stating the full name on the command line for convenience. IOW the above command is an alias to ``ploy configure jailhost-webserver``.


"Publishing" jails
------------------

Eventhough the webserver is now running, we cannot reach it from the outside, we first need to explicitly enable access. While there are several possibilites to achieve this, we will use ``ipnat``, just like in the quickstart.

So, create or edit ``host_vars/jailhost.yml`` to look like so::

	pf_nat_rules:
	    - "rdr on {{ ansible_default_ipv4.interface }} proto tcp from any to {{ ansible_default_ipv4.interface }} port 80 -> {{ hostvars['jailhost-webserver']['ploy_ip'] }} port 80"

To activate the rules, re-apply the jail host configuration for just the ``pf-conf`` tag::

	ploy configure jailhost -t pf-conf

You should now be able to access the default nginx website at the ``http://192.168.56.100`` address.


Use defaults
------------

Currently the webserver serves the default site located at ``/usr/local/www/nginx`` which is a symbolic link to ``nginx-dist``.

Now, to switch it the website located inside the ZFS filesystem we could either change the nginx configuration to point to it but in practice it can be a good idea to use default settings as much as possible and instead make the environment match the default.
*Every custom configuration file you can avoid is a potential win*.

In this particular case, let's mount the website into the default location. First we need to remove the symbolic link that has been created by the nginx start up.
Since this is truly a one-time operation (if we re-run the modified playbook against a fresh instance the symbolic link would not be created and wouldn't need to be removed) we can use ploy's ability to execute ssh commands like so::

	ploy ssh webserver "rm /usr/local/www/nginx"

Now we can change the mountpoint in ``ploy.conf``::

	[ez-instance:webserver]
	master = jailhost
	ip = 10.0.0.2
	mounts =
	    src=/tank/htdocs dst=/usr/local/www/nginx ro=true

Unfortunately, currently the only way to re-mount is to stop and start the jail in question, so let's do that::

	ploy stop webserver
	ploy start webserver

Reload the website in your browser: you should now receive a ``Forbidden`` instead of the default site because the website directory is still empty.


Fabric integration
------------------

So far we've used ansible to configure the host and the jail.
Its declarative approach is perfect for this.
But what about maintenance tasks such as updating the contents of a website?
Such tasks are a more natural fit for an *imperative* approach and ``ploy_fabric`` gives us a neat way of doing this.

Let's create a top-level file named ``fabfile.py`` with the following contents::

	from fabric import api as fab

	def upload_website():
		fab.put('htdocs/*', '/usr/jails/webserver/usr/local/www/nginx/')

Since the webserver jail only has read-access, we need to upload the website via the host (for now), so let's associate the fabric file with the host by making its entry in ``ploy.conf`` look like so::

	[ez-master:jailhost]
	instance = ploy-demo
	fabfile = ../fabfile.py

Create a simple index page::

	mkdir htdocs
	echo "Hello Berlin" >> htdocs/index.html

Then upload it::

	ploy do jailhost upload_website

and reload the website.


Exercise One
------------

Requiring write-access to the jail host in order to update the website is surely not very clever.

Your task is to create a jail named ``website_edit`` that contains a writeable mount of the website and which uses a modified version of the fabric script from above to update the contents.


Exercise Two
------------

Put the path to the website on the host into a ansible variable defined in ploy.conf and make the fabric script reference it instead of hard coding it.

You can access variables defined in ansible and ``ploy.conf`` in Fabric via its ``env`` like so::

	ansible_vars = fab.env.instance.get_ansible_variables()

The result is a dictionary populated with variables from ``group_vars``, ``host_vars`` and from within ``ploy.conf``.
However, it does *not* contain any of the Ansible facts.
For details check `ploy_fabric's documentation <http://ploy.readthedocs.org/en/latest/ploy_ansible/README.html>`_
