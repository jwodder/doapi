import argparse
import sys
from   . import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-sshkey')
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('sshkey', nargs='*')
    cmd_new = cmds.add_parser('new')
    cmd_new.add_argument('name')
    cmd_new.add_argument('pubkey', type=argparse.FileType('r'), nargs='?',
                         default=sys.stdin)
    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('sshkey', nargs='+')
    cmd_update = cmds.add_parser('update')
    cmd_update.add_argument('sshkey')
    cmd_update.add_argument('name')
    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)
    if args.cmd == 'show':
        if args.sshkey:
            util.dump(cache.get_sshkeys(args.sshkey, multiple=True))
        else:
            util.dump(client.fetch_all_sshkeys())
    elif args.cmd == 'new':
        util.dump(client.create_sshkey(args.name, args.pubkey.read().strip()))
    elif args.cmd == 'delete':
        keys = cache.get_sshkeys(args.sshkey, multiple=False)
        for k in keys:
            k.delete()
    elif args.cmd == 'update':
        key = cache.get_sshkey(args.sshkey, multiple=False)
        util.dump(key.update(args.name))
    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))

if __name__ == '__main__':
    main()