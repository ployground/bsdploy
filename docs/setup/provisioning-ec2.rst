Provisioning Amazon EC2 instances
=================================

BSDploy provides automated provisioning of `Amazon EC2 <http://aws.amazon.com/ec2/>`_ instances via the `ploy_ec2 plugin <http://ploy.readthedocs.org/en/latest/ploy_ec2/README.html>`_.

.. Note:: The plugin is not installed by default when installing BSDploy, so you need to install it additionally like so ``pip install ploy_ec2``.

Like with :doc:`Virtualbox instances <provisioning-virtualbox>` the configuration doesn't just describe existing instances but is used to create them. 

The first step is always to tell ploy where to find your AWS credentials in ``ploy.conf``::

    [ec2-master:default]
    access-key-id = ~/.aws/foo.id
    secret-access-key = ~/.aws/foo.key

Then, to define EC2 instances use the ``ec2-`` prefix, for example:

.. code-block:: console
    :linenos:

    [ec2-instance:production-backend]
    region = eu-west-1
    placement = eu-west-1a
    keypair = xxx
    ip = xxx.xxx.xxx.xxx
    instance_type = c3.xlarge
    securitygroups = production
    image = ami-c847b2bf
    user = root
    startup_script = ../startup_script

Let's go through this briefly, the full details are available at the `ploy_ec2 documentation <http://ploy.readthedocs.org/en/latest/ploy_ec2/README.html>`_:

- ``2-3`` here you set the region and placement where the instance shall reside
- ``4`` you can optionally provide a keypair (that you must create or upload to EC2 beforehand). If you do so, the key will be used to grant you access to the newly created machine. See the section below regarding the ``startup_script``.
- ``5`` if you have an Elastic IP you can specify it here and ``ploy`` will tell EC2 to assign it to the instance (if it's available)
- ``6`` check `the EC2 pricing overview <https://aws.amazon.com/ec2/pricing/#aws-element-d6f4f5f6-88e6-4f9d-ae7e-bc8af955d03e1>`_ for a description of the available instance types.

- ``7`` every EC2 instance needs to belong to a so-called security group. You can either reference an existing one or create one like so::

        [ec2-securitygroup:production]
        connections =
            tcp     22      22      0.0.0.0/0
            tcp     80      80      0.0.0.0/0
            tcp    443     443      0.0.0.0/0

- ``8`` For FreeBSD the currently best option is to use Colin Percival's excellent `daemonology AMIs for FreeBSD <http://www.daemonology.net/freebsd-on-ec2/>`_. Simply pick the ID best suited for your hardware and region from the list and you're good to go!

- ``9`` The default user for which daemonology's startup script configures SSH access (using the given ``keypair``) is named ``ec2-user`` but BSDploy's playbooks all assume ``root``, so we explicitly configure this here. Note, that this means that we *must* change the ``ec-user`` name (this happens in our own ``startup_script``, see below).

- ``10`` ``ploy_ec2`` allows us to provide a local startup script which it will upload for us using Amazon's `instance metadata <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html>`_ mechanism. Here we reference it relative to the location of ``ploy.conf``. The following example provides minimal versions of ``rc.conf`` and ``sshd_config`` which...

    - configure SSH access for root
    - install Python (needed for running the :doc:`configuration playbook </setup/configuration>`)
    - updates FreeBSD to the latest patch level upon first boot::

        #!/bin/sh
        cat << EOF > etc/rc.conf
        ec2_configinit_enable="YES"
        ec2_fetchkey_enable="YES"
        ec2_fetchkey_user="root"
        ec2_bootmail_enable="NO"
        ec2_ephemeralswap_enable="YES"
        ec2_loghostkey_enable="YES"
        ifconfig_xn0="DHCP"
        firstboot_freebsd_update_enable="YES"
        firstboot_pkgs_enable="YES"
        firstboot_pkgs_list="python27"
        dumpdev="AUTO"
        panicmail_enable="NO"
        panicmail_autosubmit="NO"
        sshd_enable="YES"
        EOF

        cat << EOF > /etc/ssh/sshd_config
        Port 22
        ListenAddress 0.0.0.0
        Subsystem sftp /usr/libexec/sftp-server
        PermitRootLogin without-password
        UseDNS no
        EOF

Now you can provision the instance by running::

    # ploy start production-backend

This will take several minutes, as the machine is started up, updates itself and reboots. Be patient, it can easily take five minutes. To check if everything is done, use ploy's status command, once the instance is fully available it should say something like this::

    # ploy status production-backend
    INFO: Instance 'production-backend' (i-xxxxx) available.
    INFO: Instance running.
    INFO: Instances DNS name ec2-xxx-xx-xx-xx.eu-west-1.compute.amazonaws.com
    INFO: Instances private DNS name ip-xxx-xx-xx-xx.eu-west-1.compute.internal
    INFO: Instances public DNS name ec2-xx-xx-xx-xx.eu-west-1.compute.amazonaws.com
    INFO: Console output available. SSH fingerprint verification possible.

Especially the last line means that the new instance is now ready.

You should now be able to log in via SSH::

    ploy ssh production-backend

.. Note:: Unlike with :doc:`plain <provisioning-plain>` or :doc:`Virtualbox <provisioning-virtualbox>` instances, daemonology's `configinit <http://www.daemonology.net/blog/2013-12-09-FreeBSD-EC2-configinit.html>`_ in conjunction with a ``startup_script`` such as the example above already perform everything we need in order to be able to run the jailhost playbooks. In other words, you can skip the  :doc:`/setup/bootstrapping` step and continue straight to :doc:`/setup/configuration`.

But before continuing on to :doc:`/setup/configuration`, let's take a look around while we're still logged in and note what hard disks and network interfaces are available. I.e. on our example machine of ``c3.xlarge`` type, the interface is named ``xn0`` and we have two SSDs of 40Gb at ``/dev/xbd1`` and ``/dev/xbd2``, but by default daemonology has already created a swap partition on the first slice (highly recommended, as most instance types don't have that much RAM), so we need to specify the second slice for our use.

This means, that to configure a jailhost on this EC2 instance we need to declare an ``ez-master`` entry in ``ploy.conf`` with the following values::

    [ez-master:production]
    instance = production-backend
    bootstrap_data_pool_devices = xbd1s2 xbd2s2

In addition, since daemonology will also update the installation to the latest patch level, we will need to explicitly tell ``ezjail`` which version to install, since by default it uses the output of ``uname`` to compute the URL for downloading the base jail but that most likely won't exist (i.e ``10.0-RELEASE-p10``). You can do this by specifying ``ezjail_install_release`` for the ``ez-master`` like so::

    ezjail_install_release = 10.0-RELEASE

With this information you are now finally and truly ready to :doc:`configure the jailhost. </setup/configuration>`.