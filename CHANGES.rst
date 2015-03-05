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
