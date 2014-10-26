Ansible integration
===================

Not only does BSDploy use `ansible playbooks <http://docs.ansible.com/playbooks.html>`_ internally to configure jail hosts (via the `ploy_ansible <https://github.com/ployground/ploy_ansible>`_ plugin), but you can use it to configure jails, too, of course.

.. note:: An important difference between using ansible *as is* and via BSDploy is that unlike ansible, BSDploy does not require (or indeed support) what ansible refers to as an `inventory file <http://docs.ansible.com/intro_inventory.html>`_ – all hosts are defined within ploy's configuration file.

You can either assign roles or a playbook file to an instance and then apply them via the ``configure`` command.


Playbook assignment
-------------------

There are two ways you can assign a playbook to an instance – either via naming convention or by using the ``playbook`` parameter.

Assigning by convention works by creating a top-level ``*.yml`` file with the same name as the instance you want to assign it to.

Keep in mind, however, that unlike when targetting instances from the command line, there is no aliassing in effect, meaning you *must* use the *full* name of the jail instance in the form of *hostname*-*jailname*, i.e. in our example ``jailhost-webserver.yml``.

The *by-convention* method is great for quick one-off custom tasks for an instance – often in the playbook you include one or more roles that perform the bulk of the work and add a few top-level tasks in the playbook that didn't warrant the overhead of a a role of their own. However, the target of the playbook is effectively hard-coded in the name of the file, so re-use is not possible.

If you want to use the same playbook for multiple instances, you can assign it by using ``playbook = PATH``, where ``PATH`` usually is a top level ``*.yml`` file.

Note that any paths are always relative to the location of the ``ploy.conf`` file, so usually you would have to refer to a top-level file like so::

	[instance:webserver1]
	...
	playbook = ../nginx.yml

	[instance:webserver2]
	...
	playbook = ../nginx.yml


Role assignment
---------------

Playbook assignment can be convenient when dealing with ad-hoc or one-off tasks but both ansible and BSDploy strongly encourage the use of `roles <http://docs.ansible.com/playbooks_roles.html#roles>`_.

Role assignment works just as you've probably guessed it by now: by using a ``roles`` parameter. Unlike with ``playbook`` you can assign more than one role. You do this by listing one role per line, indented for legibility, i.e.::

	[instance:webserver]
	roles =
		nginx
		haproxy
		zfs-snapshots

.. note:: Assignment of roles and assignment of playbooks are mutually exclusive. If you try to do both, BSDploy will raise an error.


Tags
----

When applying a playbook or roles via the ``configure`` command you can select only certain tags of them to be executed by adding the ``-t`` parameter, i.e. like so::

	ploy configure webserver -t config

To select multiple tags, pass them in comma-separated. Note that in this case you must make sure you don't add any whitespace, i.e.::

	ploy configure webserver -t config,cert


.. _dir-structure:

Directory structure
-------------------

The directory of a BSDploy environment is also an `ansible project structure <http://docs.ansible.com/playbooks_best_practices.html#directory-layout>`_ meaning, you can create and use top-level directories such as ``roles``, ``group_vars`` or even ``library``, etc. (see the link about the `ansible directory structure <http://docs.ansible.com/playbooks_best_practices.html#directory-layout>`_).
