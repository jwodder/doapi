import argparse
import sys
from   . import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-ssh-key',
                                     description='Manage DigitalOcean SSH keys')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List SSH keys',
                               description='List SSH keys')
    cmd_show.add_argument('-M', '--multiple', action='store_true',
                          help='Show multiple keys with the same name instead'
                               ' of erroring')
    cmd_show.add_argument('ssh_key', nargs='*',
                          help='ID, fingerprint, or name of a registered SSH'
                               ' key; omit to list all')

    cmd_new = cmds.add_parser('new', help='Register an SSH public key',
                              description='Register an SSH public key')
    cmd_new.add_argument('--unique', action='store_true',
                         help='Error if the name is already in use')
    cmd_new.add_argument('name', help='name for the new SSH key')
    cmd_new.add_argument('pubkey', type=argparse.FileType('r'), nargs='?',
                         default=sys.stdin,
                         help='file containing an SSH public key'
                              ' (default: stdin)')

    cmd_delete = cmds.add_parser('delete', help='Unregister an SSH key',
                                 description='Unregister an SSH key')
    cmd_delete.add_argument('-M', '--multiple', action='store_true',
                            help='Delete multiple keys with the same name'
                                 ' instead of erroring')
    cmd_delete.add_argument('ssh_key', nargs='+',
                            help='ID, fingerprint, or name of a registered SSH'
                                 ' key')

    cmd_update = cmds.add_parser('update', help='Rename an SSH key',
                                 description='Rename an SSH key')
    cmd_update.add_argument('--unique', action='store_true',
                            help='Error if the new name is already in use')
    cmd_update.add_argument('ssh_key',
                            help='ID, fingerprint, or name of a registered SSH'
                                 ' key')
    cmd_update.add_argument('name', help='new name for the SSH key')

    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)

    if args.cmd == 'show':
        if args.ssh_key:
            util.dump(cache.get_sshkeys(args.ssh_key, multiple=args.multiple,
                                                      hasM=True))
        else:
            util.dump(client.fetch_all_ssh_keys())

    elif args.cmd == 'new':
        cache.check_name_dup("sshkey", args.name, args.unique)
        util.dump(client.create_ssh_key(args.name, args.pubkey.read().strip()))

    elif args.cmd == 'delete':
        keys = cache.get_sshkeys(args.ssh_key, multiple=args.multiple,
                                               hasM=True)
        for k in keys:
            k.delete()

    elif args.cmd == 'update':
        cache.check_name_dup("sshkey", args.name, args.unique)
        key = cache.get_sshkey(args.ssh_key, multiple=False)
        util.dump(key.update_ssh_key(args.name))

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)

if __name__ == '__main__':
    main()
