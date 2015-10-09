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
            'doapi-account = doapi.cli:doapi_account',
            'doapi-action = doapi.cli:doapi_action',
            'doapi-domain = doapi.cli:doapi_domain',
            'doapi-droplet = doapi.cli:doapi_droplet',
            'doapi-image = doapi.cli:doapi_image',
            'doapi-regions = doapi.cli:doapi_regions',
            'doapi-request = doapi.cli:doapi_request',
            'doapi-sizes = doapi.cli:doapi_sizes',
            'doapi-sshkey = doapi.cli:doapi_sshkey',
        ]
    },
)
