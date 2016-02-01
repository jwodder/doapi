import argparse
import importlib
from   . import _util as util

commands = [
    ('account', 'Fetch DigitalOcean account data'),
    ('action', 'Manage DigitalOcean API actions'),
    ('domain', 'Manage DigitalOcean domains & domain records'),
    ('droplet', 'Manage DigitalOcean droplets'),
    ('floating-ip', 'Manage DigitalOcean floating IP addresses'),
    ('image', 'Manage DigitalOcean droplet images'),
    ('region', 'List available DigitalOcean droplet regions'),
    ('request', 'Perform a raw DigitalOcean API request'),
    ('size', 'List available DigitalOcean droplet sizes'),
    ('ssh-key', 'Manage DigitalOcean SSH keys'),
]

def main():
    parser = argparse.ArgumentParser(parents=[util.universal], prog='doapi')
    cmds = parser.add_subparsers(title='command', dest='cmd')
    for cmd, about in commands:
        cmdparser = cmds.add_parser(cmd, help=about, description=about)
        cmdparser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    module = importlib.import_module('.' + args.cmd.replace('-', '_'),
                                     __package__)
    module.main(args.arguments, args)

if __name__ == '__main__':
    main()
