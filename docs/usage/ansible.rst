Ansible integration
===================

Not only does BSDploy use `ansible playbooks <http://docs.ansible.com/playbooks.html>`_ internally to configure jail hosts, but you can use it to configure jails, too, of course.

.. note:: An important difference between using ansible *as is* and via BSDploy is that unlike ansible, BSDploy does not require (or indeed support) what ansible refers to as an `inventory file <http://docs.ansible.com/intro_inventory.html>`_ – all hosts are defined within ploy's configuration file.

You can either assign roles to an instance or a playbook file and then apply them via the ``configure`` command.


Playbook assignment
-------------------

There are two ways you can assign a playbook to an instance – either by naming convention or by the ``playbook`` parameter.

Assigning by convention works by creating a top-level ``*.yml`` file with the same name as the instance you want it to map to.

Keep in mind, however, that unlike when targetting instances from the command line, there is no aliassing in effect, meaning you must use the *full* name of the jail instance in the form of *hostname*-*jailname*, i.e. in our example ``jailhost-webserver.yml``.

The *by-convention* method is great for quick one-off custom tasks for an instance – often in the playbook you include one or more roles that perform the bulk of the work and add a few top-level tasks in the playbook that didn't warrant the overhead of a a role of their own. However, the target of the playbook is effectively hard-coded in the name of the file, so re-use is not possible.

If you want to use the same playbook for multiple instances, you can pass it in giving a ``playbook = PATH`` where ``PATH`` usually is a top level ``*.yml`` file.

Note that any paths are always relative to the location of the ``ploy.conf`` file, so usually you would have to refer to a top-level file like so::

	[instance:webserver]
	playbook = ../nginx.yml


Role assignment
---------------

Playbook assignment can be convenient when dealing with ad-hoc or one-off tasks but both ansible and BSDploy strongly encourage the use of `roles <http://docs.ansible.com/playbooks_roles.html#roles>`_.

Role assignment works just as you've probably guessed it by now: by using a ``roles`` parameter. Unlike with ``playbook`` you can (and often should) assign more that one role. You do this by listing one role per line, indented for clarity, i.e.::

	[instance:webserver]
	roles =
		webserver
		haproxy
		zfs-snapshots

.. note:: Assignment of roles and assignment of playbooks are mutually exclusive. If you try to do both, BSDploy will raise an error.


Directory structure
-------------------

The directory of a BSDploy environment is also an `ansible project structure <http://docs.ansible.com/playbooks_best_practices.html#id9>`_ meaning, you can (and should) create a top-level directories such as ``roles``, ``group_vars`` or even ``library``, etc. (see the link about the `ansible directory structure <http://docs.ansible.com/playbooks_best_practices.html#id9>`_).



