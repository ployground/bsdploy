Updating
========

While in theory automated systems such as ploy allow you to create new and up-to-date instances easily and thus in theory you would never have to upgrade existing instances because you would simply replace them with newer versions, in practice both jails and host systems will often have to be upgrade in place.

To support this, bsdploy provides a few helper tasks which are registered by default for jailhosts.

If you want to use them in your own, custom fabfile you must import them their to make them available, i.e. like so::

    from bsdploy.fabutils import *

You can verify this by running the `do` command with `-l`:


    # ploy do HOST -l
    Available commands:

        pkg_upgrade
        rsync
        update_flavour_pkg

You can use the `pkg_upgrade` task to keep the pkg and and the installed packages on the host up-to-date.

The `update_flavour_pkg` is useful after updating the ezjail world, so that newly created jails will have an updated version of pkg from the start. (if the pkg versions become too far apart it can happen, that new jails won't bootstrap at all, because they already fail at installing python).

See the `fabutils.py` file for more details.
