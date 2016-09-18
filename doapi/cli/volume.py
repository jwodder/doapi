import argparse
from   six.moves import map  # pylint: disable=redefined-builtin
from   .         import _util as util
from   ..        import WaitTimeoutError

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-volume',
                                     description='Manage DigitalOcean volumes')

    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List volumes',
                               description='List volumes')
    cmd_show.add_argument('volume', nargs='*',
                          help='ID of a volume; omit to list all')

    cmd_new = cmds.add_parser('new', help='Create a new volume',
                              description='Create a new volume')
    cmd_new.add_argument('-d', '--description',
                         help='Free-form description for the volume')
    cmd_new.add_argument('name', help='name for the new volume')
    cmd_new.add_argument('size', type=int, help='size in GiB of the volume')
    cmd_new.add_argument('region',
                         help='region (slug) in which to create the volume')

    cmd_delete = cmds.add_parser('delete', help='Delete a volume',
                                 description='Delete a volume')
    cmd_delete.add_argument('volume', nargs='+', help='ID of a volume')

    cmd_attach = cmds.add_parser('attach', parents=[util.waitopts],
                                 help='Attach a volume to a droplet',
                                 description='Attach a volume to a droplet')
    cmd_attach.add_argument('volume', help='ID of the volume to attach')
    cmd_attach.add_argument('droplet',
                            help='ID or name of the droplet to attach to')

    cmd_detach = cmds.add_parser('detach', parents=[util.waitopts],
                                 help='Detach a volume from a droplet',
                                 description='Detach a volume from a droplet')
    cmd_detach.add_argument('volume', help='ID of the volume to detach')
    cmd_detach.add_argument('droplet',
                            help='ID or name of the droplet to detach from')

    cmd_resize = cmds.add_parser('resize', parents=[util.waitopts],
                                 help='Resize a volume',
                                 description='Resize a volume')
    cmd_resize.add_argument('volume', help='ID of the volume to resize')
    cmd_resize.add_argument('size', type=int, help='new size in GiB')

    ### show by name and/or region

    ### attach by name
    ### detach by name
    ### resize by region & name

    ### delete by name & region

    ### act, wait, actions
    ### act on by name & region?

    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)

    if args.cmd == 'show':
        if args.tag:
            util.dump(map(client.fetch_volume, args.volume))
        else:
            util.dump(client.fetch_all_volumes())

    elif args.cmd == 'new':
        util.dump(client.create_volume(args.name, args.region, args.size,
                                       description=args.description))

    elif args.cmd == 'delete':
        vols = list(map(client.fetch_volume, args.volume))
        for v in vols:
            v.delete()

    elif args.cmd == 'attach':
        vol = client.fetch_volume(args.volume)
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = vol.attach(drop)
        if args.wait:
            try:
                act = act.wait()
            except WaitTimeoutError as e:
                act = e.in_progress[0]
        util.dump(act)

    elif args.cmd == 'detach':
        vol = client.fetch_volume(args.volume)
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = vol.detach(drop)
        if args.wait:
            try:
                act = act.wait()
            except WaitTimeoutError as e:
                act = e.in_progress[0]
        util.dump(act)

    elif args.cmd == 'resize':
        vol = client.fetch_volume(args.volume)
        act = vol.resize(args.size)
        if args.wait:
            try:
                act = act.wait()
            except WaitTimeoutError as e:
                act = e.in_progress[0]
        util.dump(act)

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)

if __name__ == '__main__':
    main()
