3.0.0 - 2022-08-17
==================

- [feature] support Python 3.10.


3.0.0b4 - 2020-09-08
====================

- [feature] support ``bootstrap-password`` option.
- [feature] allow override of ``destroygeom`` via ``bootstrap-destroygeom``.
- [feature] allow override of packages installed during bootstrap via ``bootstrap-packages``.
- [fix] correct path to devfs device in mfsbsd boostrap script.


3.0.0b3 - 2019-06-09
====================

- [feature] Python 3.x support with Ansible >= 2.4.x.
- [feature] the sysrc module supports ``dst`` option to use another file then the default ``/etc/rc.conf``.
- [change] renamed ``bootstrap-host-keys`` to ``bootstrap-ssh-host-keys``.
- [change] reintroduce ``bootstrap-ssh-fingerprints`` to allow overriding of ``ssh-fingerprints`` for bootstrapping.


3.0.0b2 - 2018-02-11
====================

- [change] ask before automatically generating missing ssh host keys during bootstrap.
- [change] the default location for ``bootstrap-files`` changed from ``[playbooks-directory]/bootstrap-files`` to ``[playbooks-directory]/[instance-uid]/bootstrap-files``.
- [change] renamed ``firstboot-update`` to ``bootstrap-firstboot-update`` to match the other variables.


3.0.0b1 - 2018-02-07
====================

- [change] switch to use ploy 2.0.0 and Ansible 2.4.x.
- [feature] the ``fabfile`` option is set if ``[instance-name]/fabfile.py`` exists when the more specific ``[master-name]-[instance-name]/fabfile.py`` doesn't exist.

- [fix]: honour the ``boottrap-packages`` setting for mfsbsd.


2.3.0 - 2017-11-13
==================

- [fix] fix pf round-robin lockups. thanks to @igalic for reporting and fixing this issue
- [feature] add ed25519 support in bootstrap needed for paramiko>=2. you should check whether you have ``ssh_host_ed25519_key*`` files on your host which you might want to copy to your bootstrap files directory alongside the other ``ssh_host_*_key*`` files
- [change] removed local rsa1 host key generation


2.2.0 - 2016-11-08
==================

- [feature] add fabric helpers to keep pkg up-to-date on the host, inside jails and for the bsdploy flavour
- [feature] add support for bootstrapping on Digital Ocean by setting `bootstrap` to `digitalocean` in the `ez-master` definition
- [fix] allow setting a non-default zfs root for ezjail by setting `jails_zfs_root` in the `ez-master` definition


2.1.0 - 2015-07-26
==================

- [feature] enable jail_parallel_start in rc.conf of jail host
- [fix] import existing zpool in ``zpool`` ansible module if the name matches
- [fix] try to attach geli device first in ``zpool`` ansible module, in case it already exists, only if that fails create it from scratch
- [fix] properly handle multiple geli encrypted devices in ``zpool`` ansible module
- [fix] also honor the ``ploy_jail_host_pkg_repository`` variable during bootstrapping (not just jailhost configuration)
- [feature] files copied during bootstrap can be encrypted using the ``ploy vault`` commands. This is useful for the private ssh host keys in ``bootstrap-files``.
- [fix] fixed setting of virtualbox defaults, so they can be properly overwritten
- [feature] added new variables: ploy_jail_host_cloned_interfaces/ploy_jail_host_default_jail_interface to give more flexiblity around network interface setup
- [change] dropped support for Ansible versions < 1.8 (supports 1.8.x and 1.9.x now)
- [fix] honour proxy setting while installing ezjail itself, not just during ezjail's install run (thanks mzs114! https://github.com/ployground/bsdploy/pull/81)


2.0.0 - 2015-03-05
==================

- [feature] add support for http proxies
- [change] deactivate pkg's *auto update* feature by default
- [feature] add support for `firstboot-freebsd-update <http://www.freshports.org/sysutils/firstboot-freebsd-update/>`_ (disabled by default)
- [change] [BACKWARDS INCOMPATIBLE] switched from ipfilter to pf - you must convert any existing ``ipnat_rules`` to the new ``pf_nat_rules``.
- [feature] provide defaults for VirtualBox instances (less boilerplate)
- [fix] set full /etc/ntp.conf instead of trying to fiddle with an existing one.
- [feature] Support configuration as non-root user (see https://github.com/ployground/bsdploy/issues/62)
- [change] switched to semantic versioning (see http://semver.org)


1.3 - 2014-11-28
================

- [deprecation] rsync_project is not working in all cases, print a warning
- [feature] added rsync helper, which is a tiny wrapper around the rsync command
- [fix] change format of /usr/local/etc/pkg/repos/FreeBSD.conf so the package
  repository is properly recognized
- [change] use quarterly package repository everywhere


1.2 - 2014-10-26
================

- [feature] provide default and by-convention assignment of fabfiles
- [doc] document provisioning of EC2 instances
- [fix] fix string escapes for geli setup in rc.conf
- [feature] make sshd listen address configurable
- [fix] fix permission of periodic scripts in zfs_auto_snapshot role
- [doc] describe how to use a http proxy for mfsBSD


1.1.1 - 2014-09-25
==================

- increase memory for virtual machines in documentation from 512MB to 1024MB
- fix escaping for jail settings in rc.conf preventing jails from starting


1.1.0 - 2014-08-13
==================

- use FreeBSD 10.0 as default for bootstrapping and documentation
- always encode result of templates as utf-8
- fix compatibility with ansible 1.7


1.0.0 - 2014-07-20
==================

- added bsdploy.fabutils with a wrapper for rsync_project
- automatically set env.shell for fabric scripts.
- generate ssh host keys locally during bootstrap if possible.
- set ``fingerprint`` option for ezjail master automatically if a ssh host key exists locally.


1.0b4 - 2014-07-08
==================

- remove custom ``ploy`` and ``ploy-ssh`` console scripts.


1.0b3 - 2014-07-07
==================

- make ``ploy_virtualbox`` an optional dependency


1.0b2 - 2014-07-07
==================

- migrate from ``mr.awsome*`` dependencies to ``ploy*``
- various bugfixes
- added tests


1.0b1 - 2014-06-17
==================

- Initial public release
