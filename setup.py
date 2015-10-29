from setuptools import setup

setup(
    name='doapi',
    version='0.1.0.dev1',
    packages=['doapi'],
    ### Does doapi.cli constitute a separate package?
    install_requires=['requests', 'six'],

    ### <https://python-packaging-user-guide.readthedocs.org/en/latest/distributing/>

    classifiers=[
        'Programming Language :: Python :: 2',
        # The use of argparse precludes support for Python 2 versions before
        # 2.7 and Python 3 versions before 3.2.
        'Programming Language :: Python :: 2.7',
    ]

    entry_points={
        "console_scripts": [
            'doapi = doapi.cli',
            'doapi-account = doapi.cli.account',
            'doapi-action = doapi.cli.action',
            'doapi-domain = doapi.cli.domain',
            'doapi-droplet = doapi.cli.droplet',
            'doapi-image = doapi.cli.image',
            'doapi-region = doapi.cli.region',
            'doapi-request = doapi.cli.request',
            'doapi-size = doapi.cli.size',
            'doapi-sshkey = doapi.cli.sshkey',
        ]
    },
)
