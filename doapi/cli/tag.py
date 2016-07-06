import argparse
from   six.moves import map  # pylint: disable=redefined-builtin
from   .         import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal], prog='doapi-tag',
                                     description='Manage DigitalOcean tags')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List tags',
                               description='List tags')
    cmd_show.add_argument('tag', nargs='*',
                          help='name of a tag; omit to list all')

    cmd_new = cmds.add_parser('new', help='Create a new tag',
                              description='Create a new tag')
    cmd_new.add_argument('name', nargs='+', help='name for the new tag')

    cmd_delete = cmds.add_parser('delete', help='Delete a tag',
                                 description='Delete a tag')
    cmd_delete.add_argument('tag', nargs='+', help='name of a tag')

    cmd_update = cmds.add_parser('update', help='Rename a tag',
                                 description='Rename a tag')
    cmd_update.add_argument('tag', help='name of a tag')
    cmd_update.add_argument('name', help='new name for the tag')

    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)

    if args.cmd == 'show':
        if args.tag:
            util.dump(map(client.fetch_tag, args.tag))
        else:
            util.dump(client.fetch_all_tags())

    elif args.cmd == 'new':
        util.dump(map(client.create_tag, args.name))

    elif args.cmd == 'delete':
        tags = list(map(client.fetch_tag, args.tag))
        for t in tags:
            t.delete()

    elif args.cmd == 'update':
        tag = client.fetch_tag(args.tag)
        util.dump(tag.update_tag(args.name))

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)

if __name__ == '__main__':
    main()
