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
    packages=['ploy'],
    install_requires=[
        'setuptools',
        'ansible',
        'mr.awsome.ansible',
        'mr.awsome.ezjail',
    ],
    entry_points="""
      [console_scripts]
      ploy = ploy:main
      pssh = mr.awsome:aws_ssh
    """)