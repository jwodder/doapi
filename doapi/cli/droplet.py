from   __future__ import print_function
import argparse
from   base64     import b64decode
from   errno      import ENOENT
from   hashlib    import md5
from   operator   import methodcaller
import sys
from   time       import time
from   six.moves  import map, range  # pylint: disable=redefined-builtin
from   .          import _util as util
from   ..base     import DropletUpgrade

unary_acts = {
    "disable-backups":           "Disable automatic backups on a droplet",
    "enable-backups":            "Enable automatic backups on a droplet",
    "enable-ipv6":               "Enable IPv6 networking on a droplet",
    "enable-private-networking": "Enable private networking on a droplet",
    "password-reset":            "Reset the root password for a droplet",
    "power-cycle":               "Forcibly powercycle a droplet",
    "power-off":                 "Forcibly power off a droplet",
    "power-on":                  "Power on a droplet",
    "reboot":                    "Attempt to gracefully reboot a droplet",
    "shutdown":                  "Attempt to gracefully shut down a droplet",
    "upgrade":                   "Upgrade a droplet",
}

unary_other = {
    'show-snapshots': ("List a droplet's snapshot images",
                       'fetch_all_snapshots'),
    'backups': ("List a droplet's backup images", 'fetch_all_backups'),
    'kernels': ('List the kernels available to a droplet', 'fetch_all_kernels'),
    'delete':  ('Delete a droplet', 'delete'),
}

create_rate = 10  # maximum number of droplets to create at once

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-droplet',
                                     description='Manage DigitalOcean droplets')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List droplets',
                               description='List droplets')
    cmd_show.add_argument('-M', '--multiple', action='store_true',
                          help='Show multiple droplets with the same name'
                               ' instead of erroring')
    cmd_show.add_argument('droplet', nargs='*',
                          help='ID or name of a droplet; omit to list all')

    cmd_new = cmds.add_parser('new', parents=[util.waitopts],
                              help='Create a new droplet',
                              description='Create a new droplet')
    cmd_new.add_argument('-I', '--image', required=True,
                         help="ID, slug, or name for the droplet's base image")
    cmd_new.add_argument('-S', '--size', required=True,
                         help="slug for the droplet's size")
    cmd_new.add_argument('-R', '--region', required=True,
                         help="slug for the droplet's region")
    cmd_new.add_argument('-B', '--backups', action='store_true',
                         help='Enable automatic backups on the new droplet')
    cmd_new.add_argument('-6', '--ipv6', action='store_true',
                         help='Enable IPv6 on the new droplet')
    cmd_new.add_argument('-P', '--private-networking', action='store_true',
                         help='Enable private networking on the new droplet')
    cmd_new.add_argument('-U', '--user-data', metavar='string|@file',
                         type=util.str_or_file,
                         help='user data for the new droplet')
    cmd_new.add_argument('-K', '--ssh-key', action='append', default=[],
                         help='ID, fingerprint, name, or local filepath of an'
                              ' SSH public key to add to the droplet')
    cmd_new.add_argument('--unique', action='store_true',
                         help='Error if the name is already in use')
    cmd_new.add_argument('name', nargs='+', help='name for the new droplet')

    util.add_actioncmds(cmds, 'droplet')

    for act in sorted(unary_acts):
        c = cmds.add_parser(act, parents=[util.waitopts], help=unary_acts[act],
                            description=unary_acts[act])
        c.add_argument('-M', '--multiple', action='store_true',
                       help='Operate on multiple droplets with the same name'
                            ' instead of erroring')
        c.add_argument('droplet', nargs='+', help='ID or name of a droplet')

    for act in sorted(unary_other):
        about = unary_other[act][0]
        c = cmds.add_parser(act, help=about, description=about)
        c.add_argument('-M', '--multiple', action='store_true',
                       help='Operate on multiple droplets with the same name'
                            ' instead of erroring')
        c.add_argument('droplet', nargs='+', help='ID or name of a droplet')

    c = cmds.add_parser('neighbors',
                        help='Show groups of droplets that are running on the'
                             ' same physical hardware',
                        description='Show groups of droplets that are running'
                                    ' on the same physical hardware')
    c.add_argument('-M', '--multiple', action='store_true',
                   help='Fetch data for multiple droplets with the same name'
                        ' instead of erroring')
    c.add_argument('droplet', nargs='*',
                   help='Only show neighbors of these droplets (specified by'
                        ' ID or name)')

    cmds.add_parser('show-upgrades',
        help='List pending droplet upgrades',
        description='List pending droplet upgrades',
    ).add_argument('--droplets', action='store_true',
                   help='Describe the droplets instead of their upgrades')

    cmd_restore = cmds.add_parser('restore', parents=[util.waitopts],
                                  help='Restore a droplet from a backup',
                                  description='Restore a droplet from a backup')
    cmd_restore.add_argument('droplet', help='ID or name of a droplet')
    cmd_restore.add_argument('backup', help='ID or name of a backup image')

    cmd_resize = cmds.add_parser('resize', parents=[util.waitopts],
                                 help='Resize a droplet',
                                 description='Resize a droplet')
    cmd_resize.add_argument('--disk', action='store_true',
                            help='Also resize the disk')
    cmd_resize.add_argument('-M', '--multiple', action='store_true',
                            help='Operate on multiple droplets with the same'
                                 ' name instead of erroring')
    cmd_resize.add_argument('size', help="slug for the droplet's new size")
    cmd_resize.add_argument('droplet', nargs='+',
                            help='ID or name of a droplet')

    cmd_rebuild = cmds.add_parser('rebuild', parents=[util.waitopts],
                                  help='Rebuild a droplet from an image',
                                  description='Rebuild a droplet from an image')
    cmd_rebuild.add_argument('-I', '--image',
                             help="ID, slug, or name of an image; defaults to"
                                  " the droplet's current image")
    cmd_rebuild.add_argument('-M', '--multiple', action='store_true',
                             help='Operate on multiple droplets with the same'
                                  ' name instead of erroring')
    cmd_rebuild.add_argument('droplet', nargs='+',
                             help='ID or name of a droplet')

    cmd_rename = cmds.add_parser('rename', parents=[util.waitopts],
                                 help='Rename a droplet',
                                 description='Rename a droplet')
    cmd_rename.add_argument('--unique', action='store_true',
                            help='Error if the name is already in use')
    cmd_rename.add_argument('droplet', help='ID or name of a droplet')
    cmd_rename.add_argument('name', help='new name for the droplet')

    cmd_snapshot = cmds.add_parser('snapshot', parents=[util.waitopts],
                                   help='Create a snapshot image of a droplet',
                                   description='Create a snapshot image of a'
                                               ' droplet')
    cmd_snapshot.add_argument('--unique', action='store_true',
                              help='Error if the name is already in use')
    cmd_snapshot.add_argument('droplet', help='ID or name of a droplet')
    cmd_snapshot.add_argument('name', help='name for the snapshot image')

    cmd_chkernel = cmds.add_parser('change-kernel', parents=[util.waitopts],
                                   help="Change a droplet's kernel",
                                   description="Change a droplet's kernel")
    cmd_chkernel.add_argument('-M', '--multiple', action='store_true',
                              help='Operate on multiple droplets with the same'
                                   ' name instead of erroring')
    cmd_chkernel.add_argument('kernel', type=int, help='ID of a kernel')
    cmd_chkernel.add_argument('droplet', nargs='+',
                              help='ID or name of a droplet')

    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)
    if args.cmd == 'show':
        if args.droplet:
            util.dump(cache.get_droplets(args.droplet, multiple=args.multiple,
                                                       hasM=True))
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
        for n in args.name:
            cache.check_name_dup("droplet", n, args.unique)
        sshkeys = []
        for kname in args.ssh_key:
            key = cache.get_sshkey(kname, multiple=False, mandatory=False)
            if key is None:
                try:
                    with open(kname) as fp:
                        pubkey = fp.read().strip()
                except IOError as e:
                    if e.errno == ENOENT:
                        util.die('{0}: no such SSH key'.format(kname))
                    else:
                        raise
                else:
                    # First see if a key with the same fingerprint already
                    # exists and, if so, use that.
                    keyparts = pubkey.split(None, 2)
                    try:
                        # <http://stackoverflow.com/a/6682934/744178>
                        fprint = md5(b64decode(keyparts[1])).hexdigest()
                        fprint = ':'.join(fprint[i:i+2]
                                          for i in range(0, len(fprint), 2))
                    except (IndexError, TypeError):
                        util.die('{0}: no such SSH key'.format(kname))
                    try:
                        key = cache.caches["sshkey"]["fingerprint"][fprint][0]
                    except LookupError:
                        if len(keyparts) > 2 and keyparts[2] != '':
                            newname = keyparts[2]
                        else:
                            newname = 'doapi-' + kname + '-' + str(int(time()))
                        cache.check_name_dup("sshkey", newname, args.unique)
                        key = client.create_ssh_key(newname, pubkey)
                        cache.add_sshkey(key)
                        print('New SSH key {0!r} registered with ID {1.id} and'
                              ' fingerprint {2}'.format(newname, key, fprint),
                              file=sys.stderr)
            sshkeys.append(key)
        if sshkeys:
            params["ssh_keys"] = sshkeys
        drops = []
        for i in range(0, len(args.name), create_rate):
            drops.extend(client.create_multiple_droplets(args.name[i:i+create_rate], **params))
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
        acts = map(methodcaller(args.cmd.replace('-', '_')), drops)
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'delete':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple,
                                                 hasM=True)
        for d in drops:
            d.delete()

    elif args.cmd in unary_other:
        util.dump(map(methodcaller(unary_other[args.cmd][1]),
                      cache.get_droplets(args.droplet, multiple=args.multiple,
                                                       hasM=True)))

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
        cache.check_name_dup("droplet", args.name, args.unique)
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.rename(args.name)
        if args.wait:
            act = act.wait()
        util.dump(act)

    elif args.cmd == 'snapshot':
        cache.check_name_dup("image", args.name, args.unique)
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
            util.dump(map(methodcaller('fetch_all_neighbors'),
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
        assert False, 'No path defined for command {0!r}'.format(args.cmd)


if __name__ == '__main__':
    main()
