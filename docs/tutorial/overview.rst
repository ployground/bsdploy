Tutorial
========


Overview
--------

This tutorial will focus on setting up a host as an all-purpose webserver, with a dedicated jail for handling the incoming traffic and redirecting it to the appropriate jails.

In it, we will also demonstrate how to setup a staging/production environment. We will start with developing the host on a virtual instance and at the end will replay the final setup against a 'production' host.

We will 

- configure a webserver jail (nginx) with a simple static overview site which contains links to the various services offered inside the jails. This step will also demonstrate the integration of Fabric scripts and configuring FreeBSD services and how to mount ZFS filesystems into jails.
- install an application that is more or less usable out-of-the-box and requires minimal configuration (transmission, a bit torrent client with a web frontend)
- create a 'production' configuration and apply the setup to it


Requirements
------------

To follow along this tutorial, you will need to have :doc:`installed bsdploy </installation>` and a running jailhost. The easiest and recommended way to achieve this is to follow along the :doc:`quickstart </quickstart>`. 
