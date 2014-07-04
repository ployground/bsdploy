Provisioning VirtualBox instances
=================================

BSDploy provides automated provisioning of `VirtualBox <https://www.virtualbox.org>`_ instances via the `ploy_virtualbox plugin <https://github.com/ployground/ploy_virtualbox>`_.

Unlike with :doc:`plain instances <provisioning-plain>` the configuration doesn't just describe existing instances but is used to create them. Consider the following entry in ``ploy.conf``::

    [vb-instance:ploy-demo]
    vm-ostype = FreeBSD_64
    vm-memory = 512
    vm-accelerate3d = off
    vm-acpi = on
    vm-rtcuseutc = on
    vm-boot1 = disk
    vm-boot2 = dvd
    vm-nic1 = nat
    vm-natpf1 = ssh,tcp,,44003,,22
    storage =
        --type dvddrive --medium ../downloads/mfsbsd-se-9.2-RELEASE-amd64.iso
        --medium vb-disk:boot

    [vb-disk:boot]
    size = 102400

VirtualBox instances are configured using the ``vb-instance`` prefix and you can set parameters of the virtual machine by prefixing them with ``vm-``. For additional details on which parameters are available and what they mean, refer to the documentation of the VirtualBox commandline tool `VBoxManage <http://www.virtualbox.org/manual/ch08.html>`_, in particualar for `VBoxManage createvm <http://www.virtualbox.org/manual/ch08.html#vboxmanage-createvm>`_ and `VBoxManage modifyvm <http://www.virtualbox.org/manual/ch08.html#vboxmanage-modifyvm>`_.

In addition to the ``vb-instance`` you will need to configure at least one storage device using a ``vb-disk`` entry which is essentially a wrapper for `VBoxManage createhd <http://www.virtualbox.org/manual/ch08.html#vboxmanage-createvdi>`_.

As you can see in the example above, you need to include the disk in the ``storage`` parameter of the ``vb-instance`` entry in order to make it available for it.

Also note, that we reference a mfsBSD boot image. Since VirtualBox won't find a bootable OS on the new drive initially, it will attempt to boot into mfsBSD.

To download the image, use ``ploy-download`` like so::

    mkdir downloads
    ploy-download http://mfsbsd.vx.sk/files/iso/9/amd64/mfsbsd-se-9.2-RELEASE-amd64.iso 4ef70dfd7b5255e36f2f7e1a5292c7a05019c8ce downloads/

Unlike ``VBoxManage`` BSDploy does not provide an explicit *create* command, instead just start the instance and if it doesn't exist already, BSDploy will create it for you on-demand::

    ploy start ploy-demo

Since the network interface is configured via DHCP, we cannot know under which IP the VM will be available. Instead the above snippet configures portforwarding, so regardless of the IP it gets via DHCP, we will access the VM via SSH using the host ``localhost`` and (in the example) port ``44003``. Adjust these values to your needs and use them during :doc:`/setup/bootstrapping`.

.. Note:: In addtion to starting a VM you can also use the ``stop`` and ``terminate`` commands..
