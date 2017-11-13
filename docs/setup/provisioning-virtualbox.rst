Provisioning VirtualBox instances
=================================

BSDploy provides automated provisioning of `VirtualBox <https://www.virtualbox.org>`_ instances via the `ploy_virtualbox plugin <https://github.com/ployground/ploy_virtualbox>`_.

.. Note:: The plugin is not installed by default when installing BSDploy, so you need to install it additionally like so ``pip install ploy_virtualbox``.


Unlike with :doc:`plain instances <provisioning-plain>` the configuration doesn't just describe existing instances but is used to create them. Consider the following entry in ``ploy.conf``::

    [vb-instance:ploy-demo]
    vm-nic2 = nat
    vm-natpf1 = ssh,tcp,,44003,,22
    storage =
        --medium vb-disk:defaultdisk
        --type dvddrive --medium http://mfsbsd.vx.sk/files/iso/10/amd64/mfsbsd-se-10.3-RELEASE-amd64.iso --medium_sha1 564758b0dfebcabfa407491c9b7c4b6a09d9603e


VirtualBox instances are configured using the ``vb-instance`` prefix and you can set parameters of the virtual machine by prefixing them with ``vm-``. For additional details on which parameters are available and what they mean, refer to `the plugin's documentation <http://ploy.readthedocs.org/en/latest/ploy_virtualbox/README.html#instances>`_ and the documentation of the VirtualBox commandline tool `VBoxManage <http://www.virtualbox.org/manual/ch08.html>`_, in particualar for `VBoxManage createvm <http://www.virtualbox.org/manual/ch08.html#vboxmanage-createvm>`_ and `VBoxManage modifyvm <http://www.virtualbox.org/manual/ch08.html#vboxmanage-modifyvm>`_.

Having said that, BSDploy provides a number of convenience defaults for each instance, so in most cases you won't need much more than in the above example.


Default hostonly network
------------------------

Unless you configure otherwise, BSDploy will tell VirtualBox to 

- create a host-only network interface named ``vboxnet0``
- assign the first network interface to that
- create a DHCP server for the address range ``192.168.56.100-254``

This means that a) during bootstrap the VM will receive a DHCP address from that range but more importantly b) you are free to assign your own static IPs from the range *below* (i.e. ``192.168.56.10``) because the existence of the VirtualBox DHCP server will ensure that that IP is reachable from the host system. This allows you to assign known, good static IP addresses to all of your VirtualBox instances.


Default disk setup
------------------

As you can see in the example above, there is a reference to a disk named ``defaultdisk`` in the ``storage`` parameter of the ``vb-instance`` entry. If you reference a disk of that name, BSDploy will automatically provision a virtual sparse disk of 100Gb size. In practice it's often best to leave that assignment in place (it's where the OS will be installed onto during bootstrap) and instead configure additional disks for data storage.


Boot images
-----------

Also note, that we reference a mfsBSD boot image above and assign it to the optical drive. By providing an external URL with a checksum, ``ploy_virtualbox`` will download that image for us (by default into ``~/.ploy/downloads/``) and connect it to the instance.


First Startup
-------------

Unlike ``VBoxManage`` BSDploy does not provide an explicit *create* command, instead just start the instance and if it doesn't exist already, BSDploy will create it for you on-demand::

    ploy start ploy-demo

Since the network interface is configured via DHCP, we cannot know under which IP the VM will be available. Instead the above snippet configures portforwarding, so regardless of the IP it gets via DHCP, we will access the VM via SSH using the host ``localhost`` and (in the example) port ``44003``. Adjust these values to your needs and use them during :doc:`/setup/bootstrapping`.

.. Note:: In addtion to starting a VM you can also use the ``stop`` and ``terminate`` commands..
