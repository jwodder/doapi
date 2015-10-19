from .         import _util as util
from ..droplet import Droplet

unary_drop_acts = {act.replace('_', '-'): getattr(Droplet, act)
                   for act in "disable_backups reboot power_cycle shutdown"
                              " power_off power_on password_reset enable_ipv6"
                              " enable_private_networking upgrade".split()}

def main():
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-droplet')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('droplet', nargs='+')

    cmd_new = cmds.add_parser('new', parents=[util.waitopts])
    cmd_new.add_argument('-i', '--image', required=True)
    cmd_new.add_argument('-s', '--size', required=True)
    cmd_new.add_argument('-r', '--region', required=True)
    cmd_new.add_argument('-B', '--backups', action='store_true')
    cmd_new.add_argument('--ipv6', action='store_true')
    cmd_new.add_argument('-P', '--private-networking', action='store_true')
    cmd_new.add_argument('-U', '--user-data')
    cmd_new.add_argument('-K', '--ssh-key', action='append', default=[])
    cmd_new.add_argument('name', nargs='+')

    cmd_wait = cmds.add_parser('wait', parents=[util.waitbase])
    cmd_wait.add_argument('-S', '--status', type=str.lower,
                          choices=['active', 'new', 'off', 'archive']
    cmd_wait.add_argument('droplet', nargs='+')

    for act in sorted(unary_drop_acts):
        cmds.add_parser(act, parents=[util.waitopts])\
            .add_argument('droplet', nargs='+')

    for act in "snapshots backups kernels delete".split():
        cmds.add_parser(act).add_argument('droplet', nargs='+')

    cmd.add_parser('neighbors').add_argument('droplet', nargs='*')
    cmd.add_parser('upgrades').add_argument('--droplets', action='store_true')

    cmd_restore = cmds.add_parser('restore', parents=[util.waitopts])
    cmd_restore.add_argument('droplet')
    cmd_restore.add_argument('backup')

    cmd_resize = cmds.add_parser('resize', parents=[util.waitopts])
    cmd_resize.add_argument('--disk', action='store_true')
    cmd_resize.add_argument('droplet')
    cmd_resize.add_argument('size')

    cmd_rebuild = cmds.add_parser('rebuild', parents=[util.waitopts])
    cmd_rebuild.add_argument('--image')
    cmd_rebuild.add_argument('droplet', nargs='+')

    cmd_rename = cmds.add_parser('rename', parents=[util.waitopts])
    cmd_rename.add_argument('droplet')
    cmd_rename.add_argument('name')

    cmd_snapshot = cmds.add_parser('snapshot', parents=[util.waitopts])
    cmd_snapshot.add_argument('droplet')
    cmd_snapshot.add_argument('name')

    cmd_chkernel = cmds.add_parser('change-kernel', parents=[util.waitopts])
    cmd_chkernel.add_argument('droplet')
    cmd_chkernel.add_argument('kernel', type=int)

    ### raw action, getting actions/last action, etc.

    args = parser.parse_args()
    client, cache = util.mkclient(args)
    if args.cmd == 'show':
        util.dump(cache.get_droplets(args.droplet, multiple=True))

    elif args.cmd == 'new':
        params = {
            "image": cache.get_image(args.image, multiple=False),
            ### TODO: Check that `args.size` and `args.region` are valid
            "size": args.size,
            "region": args.region,
            "backups": args.backups,
            "ipv6": args.ipv6,
            "private_networking": args.private_networking,
        }
        if args.user_data is not None:
            params["user_data"] = args.user_data

        ### name uniqueness

        ### SSH keys
        sshkeys = []
        for kname in args.ssh_key:
            key = cache.get_sshkey(kname, multiple=False, mandatory=True)
            if key is None:

        drops = [client.create_droplet(n, **params) for n in args.name]
        if args.wait:
            ### TODO: Dump actions as they complete
            drops = client.wait_droplets(drops, status='active')
            ### Note: This will cause problems when fetching a pre-existing
            ###       droplet that isn't active.
        util.dump(drops)

    elif args.cmd == 'wait':
        ...

    elif args.cmd in unary_drop_acts:
        # Fetch all of the droplets first so that an invalid droplet
        # specification won't cause some actions to start and others not.
        drops = cache.get_droplets(args.droplet, multiple=False)
        acts = map(unary_drop_acts[args.cmd], drops)
        if args.wait:
            ### TODO: Dump actions as they complete
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'snapshots':
        util.dump(map(Droplet.fetch_all_snapshots,
                      cache.get_droplets(args.droplet, multiple=False)))

    elif args.cmd == 'backups':
        util.dump(map(Droplet.fetch_all_backups,
                      cache.get_droplets(args.droplet, multiple=False)))

    elif args.cmd == 'kernels':
        util.dump(map(Droplet.fetch_all_kernels,
                      cache.get_droplets(args.droplet, multiple=False)))

    elif args.cmd == 'delete':
        drops = cache.get_droplets(args.droplet, multiple=False)
        for d in drops:
            d.delete()

    elif args.cmd == 'restore':
        drop = cache.get_droplet(args.droplet, multiple=False)
        img = cache.get_image(args.backup, multiple=False)
        ### Check that `img` is a backup of `drop`?
        act = drop.restore(img)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'resize':
        drop = cache.get_droplet(args.droplet, multiple=False)
        ### Check that `args.size` is an actual size?
        act = drop.resize(args.size, disk=args.disk)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'rebuild':
        drops = cache.get_droplets(args.droplet, multiple=False)
        if args.image is not None:
            img = cache.get_image(args.image, multiple=False)
            acts = [d.rebuild(img) for d in drops]
        else:
            acts = [d.rebuild(d.image) for d in drops]
        if args.wait:
            ### TODO: Dump actions as they complete
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'rename':
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.rename(args.name)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'snapshot':
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.snapshot(args.name)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'change-kernel':
        drop = cache.get_droplet(args.droplet, multiple=False)
        ### Check that `kernel` is actually a kernel?
        act = drop.change_kernel(args.kernel)
        if args.wait:
            act = act.wait()
        util.dump(act)

### neighbors
### upgrades

    else:
        assert False, 'No path defined for command %r' % (args.cmd,)


if __name__ == '__main__':
    main()
