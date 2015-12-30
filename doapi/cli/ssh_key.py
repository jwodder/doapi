import argparse
import sys
from   . import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-ssh-key')
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('-M', '--multiple', action='store_true')
    cmd_show.add_argument('ssh_key', nargs='*')
    cmd_new = cmds.add_parser('new')
    cmd_new.add_argument('--unique', action='store_true')
    cmd_new.add_argument('name')
    cmd_new.add_argument('pubkey', type=argparse.FileType('r'), nargs='?',
                         default=sys.stdin)
    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('-M', '--multiple', action='store_true')
    cmd_delete.add_argument('ssh_key', nargs='+')
    cmd_update = cmds.add_parser('update')
    cmd_update.add_argument('--unique', action='store_true')
    cmd_update.add_argument('ssh_key')
    cmd_update.add_argument('name')
    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)
    if args.cmd == 'show':
        if args.ssh_key:
            util.dump(cache.get_sshkeys(args.ssh_key, multiple=args.multiple,
                                                      hasM=True))
        else:
            util.dump(client.fetch_all_ssh_keys())
    elif args.cmd == 'new':
        if args.unique and cache.name_exists("sshkey", args.name):
            util.die('%s: name already in use' % (args.name,))
        util.dump(client.create_ssh_key(args.name, args.pubkey.read().strip()))
    elif args.cmd == 'delete':
        keys = cache.get_sshkeys(args.ssh_key, multiple=args.multiple,
                                               hasM=True)
        for k in keys:
            k.delete()
    elif args.cmd == 'update':
        if args.unique and cache.name_exists("sshkey", args.name):
            util.die('%s: name already in use' % (args.name,))
        key = cache.get_sshkey(args.ssh_key, multiple=False)
        util.dump(key.update_ssh_key(args.name))
    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))

if __name__ == '__main__':
    main()
