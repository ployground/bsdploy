# coding: utf-8
from fabric.api import env
from bsdploy.fabrics import bootstrap, fetch_assets, bootstrap_daemonology

# a plain, default fabfile for jailhosts

# shutup pyflakes
(bootstrap, fetch_assets, bootstrap_daemonology)


env.shell = '/bin/sh -c'
