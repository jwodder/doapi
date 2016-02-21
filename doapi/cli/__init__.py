import argparse
import importlib
from   . import _util as util

def main():
    parser = argparse.ArgumentParser(parents=[util.universal], prog='doapi',
                                     description='DigitalOcean API client',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='''\
Commands:
    account             Fetch DigitalOcean account data
    action              Manage DigitalOcean API actions
    domain              Manage DigitalOcean domains & domain records
    droplet             Manage DigitalOcean droplets
    floating-ip         Manage DigitalOcean floating IP addresses
    image               Manage DigitalOcean droplet images
    region              List available DigitalOcean droplet regions
    request             Perform a raw DigitalOcean API request
    size                List available DigitalOcean droplet sizes
    ssh-key             Manage DigitalOcean SSH keys
''')
    parser.add_argument('cmd', choices="account action domain droplet"
                                       " floating-ip image region request size"
                                       " ssh-key".split())
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    module = importlib.import_module('.' + args.cmd.replace('-', '_'),
                                     __package__)
    module.main(args.arguments, args)

if __name__ == '__main__':
    main()
