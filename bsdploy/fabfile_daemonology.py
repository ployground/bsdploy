# coding: utf-8
from fabric.api import env
from bsdploy.fabrics import bootstrap_daemonology as bootstrap
from bsdploy.fabrics import fetch_assets

# a plain, default fabfile for jailhosts

# shutup pyflakes
(bootstrap, fetch_assets)


env.shell = '/bin/sh -c'
