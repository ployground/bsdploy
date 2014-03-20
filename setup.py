from setuptools import setup

version = "0.1"

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
        'ansible',
        'mr.awsome.ansible',
        'mr.awsome.ezjail',
        'mr.awsome.fabric',
    ],
    entry_points="""
        [console_scripts]
        ploy = bsdploy:main
        pssh = bsdploy:ssh
        [ansible_paths]
        ploy = bsdploy:ansible_paths
        [mr.awsome.plugins]
        ploy = bsdploy:plugin
    """)