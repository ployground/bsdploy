Fabric integration
==================

.. epigraph::

    `Fabric <http://www.fabfile.org>`_ is a Python library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks.

BSDploy supports applying Fabric scripts to jails and jail hosts via the `ploy_fabric <http://ploy.readthedocs.org/en/latest/ploy_fabric.html>`_ plugin.

There are two ways you can assign a fabric file to an instance:

 - *by convention* – if the project directory contains a directory with the same name as the instance, i.e. ``jailhost`` or ``jailhost-jailname`` containing a Python file named ``fabfile.py`` and no explicit file has been given, that file is used
 - by *explicit assigning one* in ``ploy.conf``, i.e.::

    [instance:webserver]
    ...
    fabfile = ../fabfile.py


Fabfile anatomy
---------------

Let's take a look at an example ``fabfile.py``:

.. code-block:: python
    :linenos:

    from fabric import api as fab

    fab.env.shell = '/bin/sh -c'

    def info():
        fab.run('uname -a')

    def service(action='status'):
        fab.run('service nginx %s' %  action)

- (``1``) Fabric conveniently exposes all of its features in its ``api`` module, so we just import that for convenience
- (``3``) Fabric assumes ``bash``, currently we must explicitly adapt it FreeBSD's default (this may eventually be handled by a future version of BSDploy)
- (``8``) You can pass in parameters from the command line to a fabric task, see `Fabric's documentation on this <http://docs.fabfile.org/en/latest/usage/fab.html#per-task-arguments>`_ for more details.


Fabfile execution
-----------------

You can execute a task defined in that file by calling ``do``, i.e.::

    # ploy do webserver service 
    [root@jailhost-webserver] run: service nginx status
    [root@jailhost-webserver] out: nginx is running as pid 1563.

Fabric has a `relatively obtuse syntax for passing in arguments <http://docs.fabfile.org/en/latest/usage/fab.html#per-task-arguments>`_ because it supports passing to multiple hosts in a single call.

To alleviate this, ``ploy_fabric`` adds a simpler method in its ``do`` command, since that only always targets a single host.

So, in our example, to restart the webserver you could do this::

    # ploy do webserver service action=restart
    [root@jailhost-webserver] run: service nginx restart
    [root@jailhost-webserver] out: Performing sanity check on nginx configuration:
    [root@jailhost-webserver] out: nginx: the configuration file /usr/local/etc/nginx/nginx.conf syntax is ok
    [root@jailhost-webserver] out: nginx: configuration file /usr/local/etc/nginx/nginx.conf test is successful
    [root@jailhost-webserver] out: Stopping nginx.
    [root@jailhost-webserver] out: Waiting for PIDS: 1563.
    [root@jailhost-webserver] out: Performing sanity check on nginx configuration:
    [root@jailhost-webserver] out: nginx: the configuration file /usr/local/etc/nginx/nginx.conf syntax is ok
    [root@jailhost-webserver] out: nginx: configuration file /usr/local/etc/nginx/nginx.conf test is successful
    [root@jailhost-webserver] out: Starting nginx.


You can also list all available tasks with the ``-l`` parameter::

    ploy do webserver -l
    Available commands:

        info
        service
