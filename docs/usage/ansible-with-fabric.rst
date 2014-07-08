Combining Ansible and Fabric
============================

Both Ansible and Fabric are great tools, but they truly shine when used together.

A common pattern for this is that a playbook is used to set up a state against which then a fabric script is (repeatedly) executed.

For example an initial setup of an application, where a playbook takes care that all required directories are created with the proper permissions and into which then a fabric script performs an upload of the application code.


Sharing variables between playbooks and fabric scripts
------------------------------------------------------

For such a collaboration both fabric and ansible need to know *where* all of this should take place, for instance. I.e. fabric has to know the location of the directory that the playbook has created.

You can either define variables directly in ``ploy.conf`` or in group or host variables such as ``group_vars/all.yml`` or ``group_vars/webserver.yml``.

To create key/value pairs in ``ploy.conf`` that are visible to ansible, you must prefix them with ``ansible-``.


For example, you could create an entry in ploy.conf like so:

.. code-block:: ini

    [instance:webserver]
    ...
    ansible-frontend_path = /opt/foo

And then use the following snippet in a playbook:

.. code-block:: yaml

    - name: ensure the www data directory exists
      file: path={{frontend_path}} state=directory mode=775

Applying the playbook will then create the application directory as expected:

.. code-block:: console

    ploy configure webserver
    PLAY [jailhost-webserver] ***************************************************** 

    GATHERING FACTS *************************************************************** 
    ok: [jailhost-webserver]

    TASK: [ensure the www data directory exists] ********************************** 
    changed: [jailhost-webserver]

Now let's create a fabric task that uploads the contents of that website::

    def upload_website():
        ansible_vars = fab.env.instance.get_ansible_variables()
        fab.put('dist/*', ansible_vars['frontend_path'] + '/')

Notice, how we're accessing the ansible variables via Fabrics' ``env`` where ``ploy_fabrics`` has conveniently placed a ploy instance of our host.

Let's run that:

.. code-block:: console

    # ploy do webserver upload_website
    [root@jailhost-webserver] put: dist/index.html -> /opt/foo/index.html

Putting variables that you want to share between fabric and ansible into your ``ploy.conf`` is the recommended way, as it upholds the configuration file as the canonical place for all of your configuration.

However, until ploy learns how to deal with multi-line variable definitions, dealing with such requires setting them in ``group_vars/all.yml``.
