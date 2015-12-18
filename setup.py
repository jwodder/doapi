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
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='doapi@varonathe.org',
    keywords='DigitalOcean',

    #description
    #long_description
    #url (GitHub repo)

    ### <https://python-packaging-user-guide.readthedocs.org/en/latest/distributing/>

    classifiers=[
        'Programming Language :: Python :: 2',
        # The use of argparse precludes support for Python 2 versions before
        # 2.7 and Python 3 versions before 3.2.
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ],

    entry_points={
        "console_scripts": [
            'doapi = doapi.cli:main',
            'doapi-account = doapi.cli.account:main',
            'doapi-action = doapi.cli.action:main',
            'doapi-domain = doapi.cli.domain:main',
            'doapi-droplet = doapi.cli.droplet:main',
            'doapi-image = doapi.cli.image:main',
            'doapi-region = doapi.cli.region:main',
            'doapi-request = doapi.cli.request:main',
            'doapi-size = doapi.cli.size:main',
            'doapi-ssh-key = doapi.cli.ssh_key:main',
        ]
    },
)
