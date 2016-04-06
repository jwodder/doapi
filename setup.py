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

with open(join(dirname(__file__), 'README.rst')) as fp:
    long_desc = fp.read()

setup(
    name='doapi',
    version=version,
    packages=['doapi', 'doapi.cli'],
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='doapi@varonathe.org',
    keywords='DigitalOcean',
    description='DigitalOcean API library & CLI',
    long_description=long_desc,
    url='https://github.com/jwodder/doapi',

    install_requires=[
        'pyRFC3339>=1.0,<2',
        'requests>=2.2.0,<3',
        'six>=1.5.0,<2',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',

        'Programming Language :: Python :: 2',
        # The use of argparse precludes support for Python 2 versions before
        # 2.7 and Python 3 versions before 3.2.
        'Programming Language :: Python :: 2.7',

        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: System :: Systems Administration',
    ],

    entry_points={
        "console_scripts": [
            'doapi = doapi.cli:main',
            'doapi-account = doapi.cli.account:main',
            'doapi-action = doapi.cli.action:main',
            'doapi-domain = doapi.cli.domain:main',
            'doapi-droplet = doapi.cli.droplet:main',
            'doapi-floating-ip = doapi.cli.floating_ip:main',
            'doapi-image = doapi.cli.image:main',
            'doapi-region = doapi.cli.region:main',
            'doapi-request = doapi.cli.request:main',
            'doapi-size = doapi.cli.size:main',
            'doapi-ssh-key = doapi.cli.ssh_key:main',
        ]
    },
)
