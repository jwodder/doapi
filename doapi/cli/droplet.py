from   __future__ import print_function
import argparse
from   base64     import b64decode
from   errno      import ENOENT
from   hashlib    import md5
import sys
from   six.moves  import map, range
from   .          import _util as util
from   ..base     import DropletUpgrade
from   ..droplet  import Droplet

unary_acts = {
    act.replace('_', '-'): getattr(Droplet, act)
    for act in "enable_backups disable_backups reboot power_cycle shutdown"
               " power_off power_on password_reset enable_ipv6"
               " enable_private_networking upgrade".split()
}

create_rate = 10  # maximum number of droplets to create at once

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-droplet')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('droplet', nargs='*')

    cmd_new = cmds.add_parser('new', parents=[util.waitopts])
    cmd_new.add_argument('-I', '--image', required=True)
    cmd_new.add_argument('-S', '--size', required=True)
    cmd_new.add_argument('-R', '--region', required=True)
    cmd_new.add_argument('-B', '--backups', action='store_true')
    cmd_new.add_argument('--ipv6', action='store_true')
    cmd_new.add_argument('-P', '--private-networking', action='store_true')
    cmd_new.add_argument('-U', '--user-data')
    cmd_new.add_argument('-K', '--ssh-key', action='append', default=[])
    cmd_new.add_argument('--unique', action='store_true')
    cmd_new.add_argument('name', nargs='+')

    util.add_actioncmds(cmds, 'droplet')

    for act in sorted(unary_acts):
        c = cmds.add_parser(act, parents=[util.waitopts])
        c.add_argument('-M', '--multiple', action='store_true')
        c.add_argument('droplet', nargs='+')

    for act in "show-snapshots backups kernels delete".split():
        c = cmds.add_parser(act)
        c.add_argument('-M', '--multiple', action='store_true')
        c.add_argument('droplet', nargs='+')

    c = cmds.add_parser('neighbors')
    c.add_argument('-M', '--multiple', action='store_true')
    c.add_argument('droplet', nargs='*')

    cmds.add_parser('show-upgrades').add_argument('--droplets',
                                                  action='store_true')

    cmd_restore = cmds.add_parser('restore', parents=[util.waitopts])
    cmd_restore.add_argument('droplet')
    cmd_restore.add_argument('backup')

    cmd_resize = cmds.add_parser('resize', parents=[util.waitopts])
    cmd_resize.add_argument('--disk', action='store_true')
    cmd_resize.add_argument('-M', '--multiple', action='store_true')
    cmd_resize.add_argument('size')
    cmd_resize.add_argument('droplet', nargs='+')

    cmd_rebuild = cmds.add_parser('rebuild', parents=[util.waitopts])
    cmd_rebuild.add_argument('-I', '--image')
    cmd_rebuild.add_argument('-M', '--multiple', action='store_true')
    cmd_rebuild.add_argument('droplet', nargs='+')

    cmd_rename = cmds.add_parser('rename', parents=[util.waitopts])
    cmd_rename.add_argument('--unique', action='store_true')
    cmd_rename.add_argument('droplet')
    cmd_rename.add_argument('name')

    cmd_snapshot = cmds.add_parser('snapshot', parents=[util.waitopts])
    cmd_snapshot.add_argument('--unique', action='store_true')
    cmd_snapshot.add_argument('droplet')
    cmd_snapshot.add_argument('name')

    cmd_chkernel = cmds.add_parser('change-kernel', parents=[util.waitopts])
    cmd_chkernel.add_argument('-M', '--multiple', action='store_true')
    cmd_chkernel.add_argument('kernel', type=int)
    cmd_chkernel.add_argument('droplet', nargs='+')

    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)
    if args.cmd == 'show':
        if args.droplet:
            util.dump(cache.get_droplets(args.droplet, multiple=True))
        else:
            util.dump(client.fetch_all_droplets())

    elif args.cmd == 'new':
        params = {
            "image": cache.get_image(args.image, multiple=False),
            "size": args.size,
            "region": args.region,
            "backups": args.backups,
            "ipv6": args.ipv6,
            "private_networking": args.private_networking,
        }
        if args.user_data is not None:
            params["user_data"] = args.user_data
        if args.unique:
            for n in args.name:
                if cache.name_exists("droplet", n):
                    util.die('%s: name already in use' % (n,))
        sshkeys = []
        for kname in args.ssh_key:
            key = cache.get_sshkey(kname, multiple=False, mandatory=False)
            if key is None:
                try:
                    with open(kname) as fp:
                        pubkey = fp.read().strip()
                except IOError as e:
                    if e.errno == ENOENT:
                        util.die('%s: no such SSH key' % (kname,))
                    else:
                        raise
                else:
                    # First see if a key with the same fingerprint already
                    # exists and, if so, use that.
                    try:
                        # <http://stackoverflow.com/a/6682934/744178>
                        fprint = md5(b64decode(pubkey.split()[1])).hexdigest()
                        fprint = ':'.join(fprint[i:i+2]
                                          for i in range(0, len(fprint), 2))
                    except (IndexError, TypeError):
                        util.die('%s: no such SSH key' % (kname,))
                    try:
                        key = cache.caches["sshkey"]["fingerprint"][fprint]
                    except KeyError:
                        key = client.create_ssh_key(kname, pubkey)
                        cache.add_sshkey(key)
                        print('New SSH key %r registered with ID %d and'
                              ' fingerprint %s' % (kname, key.id, fprint),
                              file=sys.stderr)
            sshkeys.append(key)
        if sshkeys:
            params["ssh_keys"] = sshkeys
        drops = []
        for i in range(0, len(args.name), create_rate):
            drops.extend(client.create_droplets(args.name[i:i+create_rate],
                                                **params))
        if args.wait:
            drops = client.wait_droplets(drops, status='active')
            ### Note: This will cause problems when fetching a pre-existing
            ###       droplet that isn't active.
        util.dump(drops)

    elif args.cmd in ('act', 'actions', 'wait'):
        drops = cache.get_droplets(args.droplet, multiple=args.multiple,
                                                 hasM=True)
        util.do_actioncmd(args, client, drops)

    elif args.cmd in unary_acts:
        # Fetch all of the droplets first so that an invalid droplet
        # specification won't cause some actions to start and others not.
        drops = cache.get_droplets(args.droplet, multiple=args.multiple,
                                                 hasM=True)
        acts = map(unary_acts[args.cmd], drops)
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'show-snapshots':
        util.dump(map(Droplet.fetch_all_snapshots,
                      cache.get_droplets(args.droplet, multiple=args.multiple,
                                                       hasM=True)))

    elif args.cmd == 'backups':
        util.dump(map(Droplet.fetch_all_backups,
                      cache.get_droplets(args.droplet, multiple=args.multiple,
                                                       hasM=True)))

    elif args.cmd == 'kernels':
        util.dump(map(Droplet.fetch_all_kernels,
                      cache.get_droplets(args.droplet, multiple=args.multiple,
                                                       hasM=True)))

    elif args.cmd == 'delete':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple,
                                                 hasM=True)
        for d in drops:
            d.delete()

    elif args.cmd == 'restore':
        drop = cache.get_droplet(args.droplet, multiple=False)
        img = cache.get_image(args.backup, multiple=False)
        act = drop.restore(img)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'resize':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple,
                                                 hasM=True)
        acts = [d.resize(args.size, disk=args.disk) for d in drops]
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'rebuild':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple,
                                                 hasM=True)
        if args.image is not None:
            img = cache.get_image(args.image, multiple=False)
            acts = [d.rebuild(img) for d in drops]
        else:
            acts = [d.rebuild(d.image) for d in drops]
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'rename':
        if args.unique and cache.name_exists("droplet", args.name):
            util.die('%s: name already in use' % (args.name,))
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.rename(args.name)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'snapshot':
        if args.unique and cache.name_exists("image", args.name):
            util.die('%s: name already in use' % (args.name,))
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.snapshot(args.name)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'change-kernel':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple,
                                                 hasM=True)
        acts = [d.change_kernel(args.kernel) for d in drops]
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'neighbors':
        if args.droplet:
            util.dump(map(Droplet.fetch_all_neighbors,
                          cache.get_droplets(args.droplet,
                                             multiple=args.multiple,
                                             hasM=True)))
        else:
            util.dump(client.fetch_all_droplet_neighbors())

    elif args.cmd == 'show-upgrades':
        upgrades = client.fetch_all_droplet_upgrades()
        if args.droplets:
            util.dump(map(DropletUpgrade.fetch_droplet, upgrades))
        else:
            util.dump(upgrades)

    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))


if __name__ == '__main__':
    main()
