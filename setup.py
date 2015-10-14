from setuptools import setup

setup(
    name='doapi',
    version='0.1.0.dev1',
    package='doapi',
    install_requires=['requests'],

    ### <https://python-packaging-user-guide.readthedocs.org/en/latest/distributing/>

    entry_points={
        "console_scripts": [
            'doapi = doapi.cli',
            'doapi-account = doapi.cli.account',
            'doapi-action = doapi.cli.action',
            'doapi-domain = doapi.cli.domain',
            'doapi-droplet = doapi.cli.droplet',
            'doapi-image = doapi.cli.image',
            'doapi-regions = doapi.cli.regions',
            'doapi-request = doapi.cli.request',
            'doapi-sizes = doapi.cli.sizes',
            'doapi-sshkey = doapi.cli.sshkey',
        ]
    },
)
