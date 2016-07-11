from   __future__  import print_function
import argparse
from   base64      import b64decode
from   collections import namedtuple
from   errno       import ENOENT
from   hashlib     import md5
from   operator    import methodcaller
import sys
from   time        import time
from   six.moves   import map, range  # pylint: disable=redefined-builtin
from   .           import _util as util
from   ..          import WaitTimeoutError

UnaryCmd = namedtuple('UnaryCmd', 'help method tag_method waitable taggable')

unary_cmds = {
    "backups":                   UnaryCmd("List a droplet's backup images", 'fetch_all_backups', None, False, False),
    "delete":                    UnaryCmd('Delete a droplet', 'delete', 'delete_all_droplets', False, False),  ### no output
    "disable-backups":           UnaryCmd("Disable automatic backups on a droplet", 'disable_backups', None, True, True),
    "enable-backups":            UnaryCmd("Enable automatic backups on a droplet", 'enable_backups', None, True, True),
    "enable-ipv6":               UnaryCmd("Enable IPv6 networking on a droplet", 'enable_ipv6', None, True, True),
    "enable-private-networking": UnaryCmd("Enable private networking on a droplet", 'enable_private_networking', None, True, True),
    "kernels":                   UnaryCmd('List the kernels available to a droplet', 'fetch_all_kernels', None, False, False),
    "password-reset":            UnaryCmd("Reset the root password for a droplet", 'password_reset', None, True, False),
    "power-cycle":               UnaryCmd("Forcibly powercycle a droplet", 'power_cycle', None, True, True),
    "power-off":                 UnaryCmd("Forcibly power a droplet off", 'power_off', None, True, True),
    "power-on":                  UnaryCmd("Power a droplet on", 'power_on', None, True, True),
    "reboot":                    UnaryCmd("Attempt to gracefully reboot a droplet", 'reboot', None, True, False),
    "show-snapshots":            UnaryCmd("List a droplet's snapshot images", 'fetch_all_snapshots', None, False, False),
    "shutdown":                  UnaryCmd("Attempt to gracefully shut down a droplet", 'shutdown', None, True, True),
}

### also taggable: `snapshot`

create_rate = 10  # maximum number of droplets to create at once

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-droplet',
                                     description='Manage DigitalOcean droplets')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List droplets',
                               description='List droplets')
    cmd_show.add_argument('-M', '--multiple', action='store_true',
                          help='Show multiple droplets with the same ID or'
                               ' name')
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

    for cname, about in sorted(unary_cmds.items()):
        parents = [util.waitopts] if about.waitable else []
        c = cmds.add_parser(cname, parents=parents,
                                   help=about.help,
                                   description=about.help)
        c.add_argument('-M', '--multiple', action='store_true',
                       help='Operate on multiple droplets with the same ID or'
                            ' name')
        if about.taggable:
            c.add_argument('--tag', help='Operate on all droplets with the given tag')
            nargs = '*'
        else:
            nargs = '+'
        c.add_argument('droplet', nargs=nargs, help='ID or name of a droplet')

    c = cmds.add_parser('neighbors',
                        help='Show groups of droplets that are running on the'
                             ' same physical hardware',
                        description='Show groups of droplets that are running'
                                    ' on the same physical hardware')
    c.add_argument('-M', '--multiple', action='store_true',
                   help='Fetch data for multiple droplets with the same ID or'
                        ' name')
    c.add_argument('droplet', nargs='*',
                   help='Only show neighbors of these droplets (specified by'
                        ' ID or name)')

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
                            help='Operate on multiple droplets with the same ID'
                                 ' or name')
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
                                  ' ID or name')
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
                                   ' ID or name')
    cmd_chkernel.add_argument('kernel', type=int, help='ID of a kernel')
    cmd_chkernel.add_argument('droplet', nargs='+',
                              help='ID or name of a droplet')

    cmd_tag = cmds.add_parser('tag', help='Add a tag to a droplet',
                              description='Add a tag to a droplet')
    cmd_tag.add_argument('-M', '--multiple', action='store_true',
                         help='Tag multiple droplets with the same name instead'
                              ' of erroring')
    cmd_tag.add_argument('tag_name', help='name of a tag')
    cmd_tag.add_argument('droplet', nargs='+', help='ID or name of a droplet')

    cmd_untag = cmds.add_parser('untag', help='Remove a tag from a droplet',
                                description='Remove a tag from a droplet')
    cmd_untag.add_argument('-M', '--multiple', action='store_true',
                           help='Untag multiple droplets with the same name'
                                ' instead of erroring')
    cmd_untag.add_argument('tag_name', help='name of a tag')
    cmd_untag.add_argument('droplet', nargs='+', help='ID or name of a droplet')

    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)
    if args.cmd == 'show':
        if args.droplet:
            util.dump(cache.get_droplets(args.droplet, multiple=args.multiple))
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
            drops = util.catch_timeout(client.wait_droplets(
                drops,
                status='active',
            ))
            ### Note: This will cause problems when fetching a pre-existing
            ###       droplet that isn't active.
        util.dump(drops)

    elif args.cmd in ('act', 'actions', 'wait'):
        drops = cache.get_droplets(args.droplet, multiple=args.multiple)
        util.do_actioncmd(args, client, drops)

    elif args.cmd in unary_cmds:
        # Fetch all of the droplets first so that an invalid droplet
        # specification won't cause some actions to start and others not.
        about = unary_cmds[args.cmd]
        if about.taggable:
            if (args.tag is not None) == (args.droplet != []):
                util.die('Specify either a --tag or droplets, not both')
            elif args.tag is not None:
                tag = client.fetch_tag(args.tag)
                output = getattr(tag, about.tag_method or about.method)()
        if not about.taggable or args.tag is None:
            drops = cache.get_droplets(args.droplet, multiple=args.multiple)
            output = map(methodcaller(about.method), drops)
        if about.waitable and args.wait:
            output = util.catch_timeout(client.wait_actions(output))
        if args.cmd != 'delete':
            util.dump(output)

    elif args.cmd == 'restore':
        drop = cache.get_droplet(args.droplet, multiple=False)
        img = cache.get_image(args.backup, multiple=False)
        act = drop.restore(img)
        if args.wait:
            try:
                act = act.wait()
            except WaitTimeoutError as e:
                act = e.in_progress[0]
        util.dump(act)

    elif args.cmd == 'resize':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple)
        acts = [d.resize(args.size, disk=args.disk) for d in drops]
        if args.wait:
            acts = util.catch_timeout(client.wait_actions(acts))
        util.dump(acts)

    elif args.cmd == 'rebuild':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple)
        if args.image is not None:
            img = cache.get_image(args.image, multiple=False)
            acts = [d.rebuild(img) for d in drops]
        else:
            acts = [d.rebuild(d.image) for d in drops]
        if args.wait:
            acts = util.catch_timeout(client.wait_actions(acts))
        util.dump(acts)

    elif args.cmd == 'rename':
        cache.check_name_dup("droplet", args.name, args.unique)
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.rename(args.name)
        if args.wait:
            try:
                act = act.wait()
            except WaitTimeoutError as e:
                act = e.in_progress[0]
        util.dump(act)

    elif args.cmd == 'snapshot':
        cache.check_name_dup("image", args.name, args.unique)
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.snapshot(args.name)
        if args.wait:
            try:
                act = act.wait()
            except WaitTimeoutError as e:
                act = e.in_progress[0]
        util.dump(act)

    elif args.cmd == 'change-kernel':
        drops = cache.get_droplets(args.droplet, multiple=args.multiple)
        acts = [d.change_kernel(args.kernel) for d in drops]
        if args.wait:
            acts = util.catch_timeout(client.wait_actions(acts))
        util.dump(acts)

    elif args.cmd == 'neighbors':
        if args.droplet:
            util.dump(map(methodcaller('fetch_all_neighbors'),
                          cache.get_droplets(args.droplet,
                                             multiple=args.multiple)))
        else:
            util.dump(client.fetch_all_droplet_neighbors())

    elif args.cmd == 'tag':
        tag = client.fetch_tag(args.tag_name)
        drops = cache.get_droplets(args.droplet, multiple=args.multiple)
        tag.add(*drops)

    elif args.cmd == 'untag':
        tag = client.fetch_tag(args.tag_name)
        drops = cache.get_droplets(args.droplet, multiple=args.multiple)
        tag.remove(*drops)

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)


if __name__ == '__main__':
    main()
