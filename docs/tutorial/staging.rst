Staging
=======

So far we have developed our setup against a virtual machine which allowed us to experiment safely.
Now it's time to deploy the setup in production.

Principally, there are two possible approaches to this with ploy:

- either define multiple hosts in one configuration or
- use two separate configurations for each scenario

In practice it's more practical to split the configuration, as it allows to re-use instances more easily.

As a rule-of-thumb, if you ever need to configure two scenarios simultenously or either of the hosts need to communicate with each other, you should use a single configuration with multiple hosts (i.e. if you're configuring a cluster) but if you're setting up  mutually exclusive, isolated scenarios such as staging vs. production you should use two different configurations.

Another benefit of using two configurations is that you need to explicitly reference the non-default configuration which minimizes accidental modification of i.e. production hosts.

In this tutorial we will use a second VirtualBox instances to simulate a production environment but in actual projects you would more likely define either plain instances or EC2 instances.

To create a 'production' environment, create an additional configuration file ``etc/production.conf`` with the following contents::

    [global]
    extends = ploy.conf

    [vb-instance:demo-production]
    vm-nic2 = nat
    vm-natpf2 = ssh,tcp,,44004,,22
    storage =
        --type dvddrive --medium ../downloads/mfsbsd-se-9.2-RELEASE-amd64.iso
        --medium vb-disk:boot

    [ez-master:jailhost]
    instance = demo-production

Now we can start up the 'production' provider and run through the identical bootstrapping process as in the quickstart, except that we explicitly reference the production configuration::

    ploy -c etc/production.conf start demo-production

However, before we can bootstrap we need to import the ``bootstrap`` into our custom fabric file – this is because bootstrapping is internally implemented as a fabric task.

Add the following import statement to your fabfile::

    from bsdploy.fabfile_mfsbsd import bootstrap

Now we can follow through::

    ploy -c etc/production.conf bootstrap
    ploy -c etc/production.conf configure jailhost

