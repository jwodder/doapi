import argparse
from   six.moves import map  # pylint: disable=redefined-builtin
from   .         import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-floating-ip',
                                     description='Manage DigitalOcean floating'
                                                 ' IP addresses')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List floating IPs',
                               description='List floating IPs')
    cmd_show.add_argument('ip', nargs='*',
                          help='a floating IP address; omit to list all')

    cmd_new = cmds.add_parser('new', parents=[util.waitopts],
                              help='Create a new floating IP address',
                              description='Create a new floating IP address')
    newopts = cmd_new.add_mutually_exclusive_group(required=True)
    newopts.add_argument('-D', '--droplet',
                         help='ID or name of droplet to assign the new IP to')
    newopts.add_argument('-R', '--region',
                         help='slug of region to reserve the new IP to')

    cmd_assign = cmds.add_parser('assign', parents=[util.waitopts],
                                 help='Assign a floating IP to a droplet',
                                 description='Assign a floating IP to a droplet')
    cmd_assign.add_argument('ip', help='a floating IP address')
    cmd_assign.add_argument('droplet', help='ID or name of a droplet')

    cmd_unassign = cmds.add_parser('unassign', parents=[util.waitopts],
                                   help='Unassign a floating IP',
                                   description='Unassign a floating IP')
    cmd_unassign.add_argument('ip', nargs='+', help='a floating IP address')

    cmd_delete = cmds.add_parser('delete', help='Delete a floating IP',
                                 description='Delete a floating IP')
    cmd_delete.add_argument('ip', nargs='+', help='a floating IP address')

    util.add_actioncmds(cmds, 'ip', multiple=False)
    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)

    if args.cmd == 'show':
        if args.ip:
            util.dump(util.rmdups(map(client.fetch_floating_ip, map(maybeInt, args.ip)), 'floating IP', 'ip'))
        else:
            util.dump(client.fetch_all_floating_ips())

    elif args.cmd == 'new':
        if args.droplet is not None:
            drop = cache.get_droplet(args.droplet, multiple=False)
            newip = client.create_floating_ip(droplet_id=drop)
        else:
            newip = client.create_floating_ip(region=args.region)
        if args.wait:
            list(client.wait_actions(newip.fetch_all_actions()))
            newip = newip.fetch()
        util.dump(newip)

    elif args.cmd == 'assign':
        floip = client.fetch_floating_ip(maybeInt(args.ip))
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = floip.assign(drop)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'unassign':
        floips = util.rmdups(map(client.fetch_floating_ip, map(maybeInt, args.ip)), 'floating IP', 'ip')
        acts = [fi.unassign() for fi in floips]
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'delete':
        floips = util.rmdups(map(client.fetch_floating_ip, map(maybeInt, args.ip)), 'floating IP', 'ip')
        for fi in floips:
            fi.delete()

    elif args.cmd in ('act', 'actions', 'wait'):
        floips = util.rmdups(map(client.fetch_floating_ip, map(maybeInt, args.ip)), 'floating IP', 'ip')
        util.do_actioncmd(args, client, floips)

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)

def maybeInt(s):
    try:
        return int(s)
    except ValueError:
        return s

if __name__ == '__main__':
    main()
