from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = "0.1a3"

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
        'mr.awsome>=1.0rc7',
        'mr.awsome.ansible>=1.0b4',
        'mr.awsome.ezjail>=1.0b6',
        'mr.awsome.fabric>=1.0b3',
    ],
    extras_require={
        'development': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'flake8',
            'jarn.mkrelease',
            'pytest >= 2.4.2',
            'py >= 1.4.17',
            'pytest-flakes',
            'pytest-pep8',
            'pytest-cov',
            'tox',
            'mock',
            'setuptools-git',
        ],
    },
    entry_points="""
        [console_scripts]
        ploy = bsdploy:ploy
        ploy-ssh = bsdploy:ploy_ssh
        ploy-download = download:run
        [ansible_paths]
        ploy = bsdploy:ansible_paths
        [mr.awsome.plugins]
        ploy = bsdploy:plugin
    """)
