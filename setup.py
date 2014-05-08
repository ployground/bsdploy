from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = "0.1alpha1"

setup(
    version=version,
    description="A tool to provision, configure and maintain FreeBSD jails",
    name="bsdploy",
    author='Tom Lazar',
    author_email='tom@tomster.org',
    url='http://github.com/tomster/bsdploy',
    include_package_data=True,
    zip_safe=False,
    packages=['bsdploy'],
    install_requires=[
        'setuptools',
        'Fabric<1.8.3',
        'ansible<1.6',
        'mr.awsome.ansible',
        'mr.awsome.ezjail',
        'mr.awsome.fabric',
    ],
    entry_points="""
        [console_scripts]
        ploy = bsdploy:ploy
        pssh = bsdploy:ploy_ssh
        [ansible_paths]
        ploy = bsdploy:ansible_paths
        [mr.awsome.plugins]
        ploy = bsdploy:plugin
    """)
