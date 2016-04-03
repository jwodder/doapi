import argparse
from   itertools import chain
from   six.moves import map  # pylint: disable=redefined-builtin
from   .         import _util as util
from   ..action  import Action

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-action',
                                     description='Manage DigitalOcean API'
                                                 ' actions')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List actions',
                               description='List actions')
    showopts = cmd_show.add_mutually_exclusive_group()
    showopts.add_argument('--last', action='store_true',
                          help='Show only the most recent action')
    showopts.add_argument('--in-progress', action='store_true',
                          help='Show all in-progress actions')
    cmd_show.add_argument('action', nargs='*', type=int,
                          help='ID of an action; omit to list all')

    cmd_wait = cmds.add_parser('wait', parents=[util.waitbase],
                               help='Wait for an action to complete',
                               description='Wait for an action to complete')
    cmd_wait.add_argument('action', nargs='*', type=int,
                          help='ID of an action; omit to wait on all in'
                               ' progress')

    cmd_resource = cmds.add_parser('resource',
                                   help='Show the resource that an action'
                                        ' operated on',
                                   description='''\
Show the resource that an action operated on.  Resources that no longer exist
are shown as `null`.''')
    resopts = cmd_resource.add_mutually_exclusive_group()
    resopts.add_argument('--last', action='store_true',
                         help='Show only the most recent action')
    resopts.add_argument('--in-progress', action='store_true',
                         help='Show all in-progress actions')
    cmd_resource.add_argument('action', nargs='*', type=int,
                              help='ID of an action; omit to list all')

    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)

    if args.cmd == 'show':
        if args.last:
            if args.action:
                util.die('--last and action arguments are mutually exclusive')
            util.dump(client.fetch_last_action())
        elif args.in_progress:
            if args.action:
                util.die('--in-progress and action arguments are mutually'
                         ' exclusive')
            util.dump(all_in_progress(client))
        elif args.action:
            util.dump(util.rmdups(map(client.fetch_action, args.action),
                                  'action'))
        else:
            util.dump(client.fetch_all_actions())

    elif args.cmd == 'wait':
        if args.action:
            acts = util.rmdups(map(client.fetch_action, args.action),
                               'action')
        else:
            acts = all_in_progress(client)
        util.dump(client.wait_actions(acts))

    elif args.cmd == 'resource':
        if args.last:
            if args.action:
                util.die('--last and action arguments are mutually exclusive')
            util.dump(client.fetch_last_action().fetch_resource())
        else:
            if args.in_progress:
                if args.action:
                    util.die('--in-progress and action arguments are mutually'
                             ' exclusive')
                acts = all_in_progress(client)
            elif args.action:
                acts = util.rmdups(map(client.fetch_action, args.action),
                                   'action')
            else:
                util.die('You must specify one of --last, --in-progress, or'
                         ' one or more actions')
            util.dump(map(Action.fetch_resource, acts))

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)

def all_in_progress(client):
    return util.currentActions(chain(client.fetch_all_droplets(),
                                     ### TODO: This assumes that only private
                                     ### images can be acted on.  Confirm this.
                                     client.fetch_all_private_images(),
                                     client.fetch_all_floating_ips()))
    ### TODO: If an object is in the process of being deleted,
    ### `fetch_current_action` may error out.  Handle this.

if __name__ == '__main__':
    main()
