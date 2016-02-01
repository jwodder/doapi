import argparse
from   . import _util as util

def main():
    parser = argparse.ArgumentParser(parents=[util.universal], prog='doapi')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_account = cmds.add_parser('account',
                                  help='Fetch DigitalOcean account data',
                                  description='Fetch DigitalOcean account data')
    cmd_account.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_action = cmds.add_parser('action',
                                 help='Manage DigitalOcean API actions',
                                 description='Manage DigitalOcean API actions')
    cmd_action.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_domain = cmds.add_parser('domain',
                                 help='Manage DigitalOcean domains'
                                      ' & domain records',
                                 description='Manage DigitalOcean domains'
                                             ' & domain records')
    cmd_domain.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_droplet = cmds.add_parser('droplet',
                                  help='Manage DigitalOcean droplets',
                                  description='Manage DigitalOcean droplets')
    cmd_droplet.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_floating_ip = cmds.add_parser('floating-ip',
                                      help='Manage DigitalOcean floating'
                                                  ' IP addresses',
                                      description='Manage DigitalOcean floating'
                                                  ' IP addresses')
    cmd_floating_ip.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_image = cmds.add_parser('image',
                                help='Manage DigitalOcean droplet images',
                                description='Manage DigitalOcean droplet'
                                            ' images')
    cmd_image.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_region = cmds.add_parser('region',
                                 help='List available DigitalOcean'
                                      ' droplet regions',
                                 description='List available DigitalOcean'
                                             ' droplet regions')
    cmd_region.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_request = cmds.add_parser('request',
                                  help='Perform a raw DigitalOcean API request',
                                  description='Perform a raw DigitalOcean'
                                              ' API request')
    cmd_request.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_size = cmds.add_parser('size',
                               help='List available DigitalOcean droplet sizes',
                               description='List available DigitalOcean'
                                           ' droplet sizes')
    cmd_size.add_argument('arguments', nargs=argparse.REMAINDER)

    cmd_ssh_key = cmds.add_parser('ssh-key',
                                  help='Manage DigitalOcean SSH keys',
                                  description='Manage DigitalOcean SSH keys')
    cmd_ssh_key.add_argument('arguments', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    ### TODO: Figure out a shorter way to write this:
    if args.cmd == 'account':
        from .account import main as main2
    elif args.cmd == 'action':
        from .action import main as main2
    elif args.cmd == 'domain':
        from .domain import main as main2
    elif args.cmd == 'droplet':
        from .droplet import main as main2
    elif args.cmd == 'floating-ip':
        from .floating_ip import main as main2
    elif args.cmd == 'image':
        from .image import main as main2
    elif args.cmd == 'region':
        from .region import main as main2
    elif args.cmd == 'request':
        from .request import main as main2
    elif args.cmd == 'size':
        from .size import main as main2
    elif args.cmd == 'ssh-key':
        from .ssh_key import main as main2
    else:
        assert False, 'No path defined for command %r' % (args.cmd,)
    main2(args.arguments, args)

if __name__ == '__main__':
    main()
