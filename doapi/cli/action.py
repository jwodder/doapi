import argparse
from   itertools import chain
from   six.moves import map
from   .         import _util as util
from   ..action  import Action

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-action',
                                     description='Manage DigitalOcean API'
                                                 ' actions')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show')
    showopts = cmd_show.add_mutually_exclusive_group()
    showopts.add_argument('--last', action='store_true')
    showopts.add_argument('--current', action='store_true')
    cmd_show.add_argument('action', nargs='*', type=int)

    cmd_wait = cmds.add_parser('wait', parents=[util.waitbase])
    cmd_wait.add_argument('action', nargs='*', type=int)

    cmd_resource = cmds.add_parser('resource')
    resopts = cmd_resource.add_mutually_exclusive_group(required=True)
    resopts.add_argument('--last', action='store_true')
    resopts.add_argument('--current', action='store_true')
    cmd_resource.add_argument('action', nargs='*', type=int)

    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)

    if args.cmd == 'show':
        if args.last:
            if args.action:
                util.die('--last and action arguments are mutually exclusive')
            util.dump(client.fetch_last_action())
        elif args.current:
            if args.action:
                util.die('--current and action arguments are mutually'
                         ' exclusive')
            util.dump(all_in_progress(client))
        elif args.action:
            util.dump(map(client.fetch_action, args.action))
        else:
            util.dump(client.fetch_all_actions())

    elif args.cmd == 'wait':
        if args.action:
            acts = args.action
        else:
            acts = all_in_progress(client)
        util.dump(client.wait_actions(acts))

    elif args.cmd == 'resource':
        if args.last:
            if args.action:
                util.die('--last and action arguments are mutually exclusive')
            util.dump(client.fetch_last_action().fetch_resource())
        else:
            if args.current:
                if args.action:
                    util.die('--current and action arguments are mutually'
                             ' exclusive')
                acts = all_in_progress(client)
            elif args.action:
                acts = map(client.fetch_action, args.action)
            else:
                util.die('You must specify one of --last, --current, or one or'
                         ' more actions')
            util.dump(map(Action.fetch_resource, acts))

    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))

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
