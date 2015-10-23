import argparse
from   . import _util as util

def main():
    parser = argparse.ArgumentParser(parents=[util.universal], prog='doapi')
    parser.add_argument('command', choices="account action domain droplet"
                                           " floating-ip image region request"
                                           " size sshkey".split())
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    ### Figure out a shorter way to write this:
    if args.command == 'account':
        from .account import main as main2
    ###elif args.command == 'action':
    ###    from .action import main as main2
    ###elif args.command == 'domain':
    ###    from .domain import main as main2
    ###elif args.command == 'droplet':
    ###    from .droplet import main as main2
    elif args.command == 'floating-ip':
        from .floating_ip import main as main2
    ###elif args.command == 'image':
    ###    from .image import main as main2
    elif args.command == 'region':
        from .region import main as main2
    elif args.command == 'request':
        from .request import main as main2
    elif args.command == 'size':
        from .size import main as main2
    elif args.command == 'sshkey':
        from .sshkey import main as main2
    else:
        raise RuntimeError('No path defined for command %r' % (args.command,))
    main2(args.arguments, args)

if __name__ == '__main__':
    main()
