BSDploy is a tool to provision, configure and maintain FreeBSD jails.

Under the hood it uses `mr.awsome <https://pypi.python.org/pypi/mr.awsome>`_ for provisioning, `ansible <http://ansible.cc>`_ for configuration and `fabric <http://fabfile.org>`_ for maintenance.


TODO
====

 - make rc.conf a template (to support non-DHCP jailhost scenario)
 - allow for offline installation of ezjail
 - allow for offline installation of pkgng
 - include poudriere support
 - eliminate need for proxycommand, proxyhost and hooks entries for jail configuration in ploy.conf
 - make the private network for the jails configurable (the hard coded 10.0.0.x is not always desirable)