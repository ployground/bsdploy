1.1.2 - Unreleased
==================

- fix string escapes for geli setup in rc.conf
- fix permission of periodic scripts in zfs_auto_snapshot role


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
