from   os.path    import dirname, join
import re
from   setuptools import setup

with open(join(dirname(__file__), 'doapi', '__init__.py')) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError('Unable to find own __version__ string')

setup(
    name='doapi',
    version=version,
    packages=['doapi', 'doapi.cli'],
    install_requires=['requests', 'six'],

    ### <https://python-packaging-user-guide.readthedocs.org/en/latest/distributing/>

    classifiers=[
        'Programming Language :: Python :: 2',
        # The use of argparse precludes support for Python 2 versions before
        # 2.7 and Python 3 versions before 3.2.
        'Programming Language :: Python :: 2.7',
    ],

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
