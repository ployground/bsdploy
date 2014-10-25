Transmission
============

This part of the tutorial will demonstrate how to install and configure an existing web application.


Using Ansible Roles
-------------------

Unlike with the webserver from the previous example we *will* create a custom configuration, so instead of littering our top level directory with yet more playbooks and templates we will configure this instance using a role.

Let's first create the required structure::

    mkdir -p roles/transmission/tasks
    mkdir -p roles/transmission/templates
    mkdir -p roles/transmission/handlers

Populate them with a settings template in ``roles/transmission/templates/settings.json``:

.. code-block:: json

    {
        "alt-speed-up": 50,
        "alt-speed-down": 200,
        "speed-limit-down": 5000,
        "speed-limit-down-enabled": true,
        "speed-limit-up": 100,
        "speed-limit-up-enabled": true,
        "start-added-torrents": true,
        "trash-original-torrent-files": true,
        "watch-dir": "{{download_dir}}",
        "watch-dir-enabled": true,
        "rpc-whitelist":  "127.0.0.*,10.0.*.*",
        "ratio-limit": 1.25,
        "ratio-limit-enabled": true
    }

And in ``roles/transmission/handlers/main.yml``:

.. code-block:: yaml

    ---
    - name: restart transmission
      service: name=transmission state=restarted

And finally in ``roles/transmission/tasks/main.yml``:

.. code-block:: yaml

    - name: Ensure helper packages are installed
      pkgng: name={{ item }} state=present
      with_items:
      - transmission-daemon
      - transmission-web
    - name: Setup transmission to start on boot
      service: name=transmission enabled=yes
    - name: Configure transmission
      template: src=settings.json dest=/usr/local/etc/transmission/home/settings.json backup=yes owner=transmission
      notify:
        - restart transmission

The above tasks should look pretty familiar by now:

- install the required packages (this time it's more than one and we demonstrate the ``with_items`` method)
- enable it in ``rc.conf``
- Finally, as a new technique we upload a settings file as a template and...
- ... use ansible's *handlers* to make sure that the service is reloaded every time we change its settings.


Exercise One
------------

Publish the transmission daemon's web UI at ``http://192.168.56.100/transmission``.

.. note:: Proxying to transmission can be a bit finicky as it requires certain CRSF protection headers, so here's a small spoiler/hint.

This is the required nginx configuration to proxy to transmission::

    location /transmission {
        proxy_http_version  1.1;
        proxy_set_header    Connection "";
        proxy_pass_header   X-Transmission-Session-Id;
        proxy_pass          http://transmissionweb;
        proxy_redirect      off;
        proxy_buffering     off;
        proxy_set_header    Host            $host;
        proxy_set_header    X-Real-IP       $remote_addr;
    }


Exercise Two
------------

Publish the downloads directory via nginx so users can download finished torrents from ``http://192.168.56.100/downloads``.

Do this by configuring an additional jail that has read-only access to the download directory and publishes using its own nginx which is then targetted by the webserver jail.
