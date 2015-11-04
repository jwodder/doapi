import argparse
from   six.moves import map
from   .         import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-domain')
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('domain', nargs='*')
    cmd_new = cmds.add_parser('new')
    cmd_new.add_argument('domain')
    cmd_new.add_argument('ip_address')
    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('domain', nargs='+')
    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)
    if args.cmd == 'show':
        if args.domain:
            util.dump(map(client.fetch_domain, args.domain))
        else:
            util.dump(client.fetch_all_domains())
    elif args.cmd == 'new':
        util.dump(client.create_domain(args.domain, args.ip_address))
    elif args.cmd == 'delete':
        domains = list(map(client.fetch_domain, args.domain))
        for d in domains:
            d.delete()
    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))

if __name__ == '__main__':
    main()
