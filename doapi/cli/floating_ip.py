import argparse
from   six.moves import map
from   .         import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-floating-ip')
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('ip', nargs='*')
    cmd_new = cmds.add_parser('new')
    newopts = cmd_new.add_mutually_exclusive_group(required=True)
    newopts.add_argument('-D', '--droplet')
    newopts.add_argument('-R', '--region')
    cmd_assign = cmds.add_parser('assign')
    cmd_assign.add_argument('ip')
    cmd_assign.add_argument('droplet')
    cmd_unassign = cmds.add_parser('unassign')
    cmd_unassign.add_argument('ip', nargs='+')
    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('ip', nargs='+')
    util.add_actioncmds(cmds, 'ip')
    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)
    if args.cmd == 'show':
        if args.ip:
            util.dump(map(client.fetch_floating_ip, map(maybeInt, args.ip)))
        else:
            util.dump(client.fetch_all_floating_ips())
    elif args.cmd == 'new':
        if args.droplet is not None:
            drop = cache.get_droplet(args.droplet, multiple=False)
            newip = client.create_floating_ip(droplet_id=drop)
        else:
            ### Check that `args.region` is an actual region?
            newip = client.create_floating_ip(region=args.region)
        util.dump(newip)
    elif args.cmd == 'assign':
        floip = client.fetch_floating_ip(maybeInt(args.ip))
        drop = cache.get_droplet(args.droplet, multiple=False)
        util.dump(floip.assign(drop))
    elif args.cmd == 'unassign':
        floips = map(client.fetch_floating_ip, map(maybeInt, args.ip))
        util.dump([fi.unassign() for fi in floips])
    elif args.cmd == 'delete':
        floips = map(client.fetch_floating_ip, map(maybeInt, args.ip))
        for fi in floips:
            fi.delete()
    elif args.cmd in ('act', 'actions', 'wait'):
        floips = map(client.fetch_floating_ip, map(maybeInt, args.ip))
        util.do_actioncmd(args, client, floips)
    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))

def maybeInt(s):
    try:
        return int(s)
    except ValueError:
        return s

if __name__ == '__main__':
    main()
