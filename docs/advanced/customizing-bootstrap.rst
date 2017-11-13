Customizing bootstrap
=====================

Currently the bootstrap API isn't ready for documentation and general use.
In case you want to mess with it anyway, here are some things which will be safe to do.


mfsBSD http proxy example
-------------------------

If you are setting up many virtual machines for testing, then a caching http proxy to reduce the downloads comes in handy.
You can achieve that by using `polipo <http://www.pps.univ-paris-diderot.fr/~jch/software/polipo/>`_ on the VM host and the following changes.

First you need a custom fabfile:

.. code-block:: python

    from bsdploy.fabfile_mfsbsd import _bootstrap, _mfsbsd
    from fabric.api import env, hide, run, settings
    from ploy.config import value_asbool


    def bootstrap(**kwargs):
        with _mfsbsd(env, kwargs):
            reboot = value_asbool(env.instance.config.get('bootstrap-reboot', 'true'))
            env.instance.config['bootstrap-reboot'] = False
            run('echo setenv http_proxy http://192.168.56.1:8123 >> /etc/csh.cshrc')
            run('echo http_proxy=http://192.168.56.1:8123 >> /etc/profile')
            run('echo export http_proxy >> /etc/profile')
            _bootstrap()
            run('echo setenv http_proxy http://192.168.56.1:8123 >> /mnt/etc/csh.cshrc')
            run('echo http_proxy=http://192.168.56.1:8123 >> /mnt/etc/profile')
            run('echo export http_proxy >> /mnt/etc/profile')
            if reboot:
                with settings(hide('warnings'), warn_only=True):
                    run('reboot')

For the ezjail initialization you have to add the following setting with a FreeBSD http mirror of your choice to your jail host config in ``ploy.conf``::

    ansible-ploy_ezjail_install_host = http://ftp4.de.freebsd.org

The ``_mfsbsd`` context manager takes care of setting the ``bootstrap-host-keys`` etc for mfsBSD.
The ``_bootstrap`` function then runs the regular bootstrapping.

For the jails you can use a startup script like this:

.. code-block:: sh

    #!/bin/sh
    exec 1>/var/log/startup.log 2>&1
    chmod 0600 /var/log/startup.log
    set -e
    set -x
    echo setenv http_proxy http://192.168.56.1:8123 >> /etc/csh.cshrc
    echo http_proxy=http://192.168.56.1:8123 >> /etc/profile
    echo export http_proxy >> /etc/profile
    http_proxy=http://192.168.56.1:8123
    export http_proxy
    pkg install python27
