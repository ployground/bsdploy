from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = "1.0b2-dev"

setup(
    version=version,
    description="A tool to provision, configure and maintain FreeBSD jails",
    name="bsdploy",
    author='Tom Lazar',
    author_email='tom@tomster.org',
    url='http://github.com/ployground/bsdploy',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
    ],
    license='Beerware Licence',
    zip_safe=False,
    packages=['bsdploy'],
    install_requires=[
        'PyYAML',
        'jinja2',
        'setuptools',
        'mr.awsome>=1.0rc8',
        'mr.awsome.ansible>=1.0b5',
        'mr.awsome.ec2>=1.0b2',
        'mr.awsome.ezjail>=1.0b7',
        'mr.awsome.fabric>=1.0b3',
        'mr.awsome.virtualbox>=1.0b1',
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
