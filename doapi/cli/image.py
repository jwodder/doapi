import argparse
from   six.moves import map  # pylint: disable=redefined-builtin
from   .         import _util as util
from   ..image   import Image

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-image',
                                     description='Manage DigitalOcean droplet'
                                                 ' images')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List images',
                               description='List images')
    showopts = cmd_show.add_mutually_exclusive_group()
    showopts.add_argument('--distribution', action='store_true',
                          help='List distribution images')
    showopts.add_argument('--application', action='store_true',
                          help='List application images')
    showopts.add_argument('--type',
                          help='List all images of the given type'
                               ' (usually "distribution" or "application")')
    showopts.add_argument('--private', action='store_true',
                          help="List all of the user's private images")
    cmd_show.add_argument('-M', '--multiple', action='store_true',
                          help='Show multiple images with the same name instead'
                               ' of erroring')
    cmd_show.add_argument('image', nargs='*',
                          help='ID, slug, or name of an image; omit to list all')

    cmd_delete = cmds.add_parser('delete', help='Delete an image',
                                 description='Delete an image')
    cmd_delete.add_argument('-M', '--multiple', action='store_true',
                            help='Delete multiple images with the same name'
                                 ' instead of erroring')
    cmd_delete.add_argument('image', nargs='+',
                            help='ID, slug, or name of an image')

    cmd_update = cmds.add_parser('update', help='Rename an image',
                                 description='Rename an image')
    cmd_update.add_argument('--unique', action='store_true',
                            help='Error if the new name is already in use')
    cmd_update.add_argument('image', help='ID, slug, or name of an image')
    cmd_update.add_argument('name', help='new name for the image')

    cmd_transfer = cmds.add_parser('transfer', parents=[util.waitopts],
                                   help='Transfer images to another region',
                                   description='Transfer images to another region')
    cmd_transfer.add_argument('-M', '--multiple', action='store_true',
                              help='Transfer multiple images with the same name'
                                   ' instead of erroring')
    cmd_transfer.add_argument('region',
                              help='slug of the region to transfer images to')
    cmd_transfer.add_argument('image', nargs='+',
                              help='ID, slug, or name of an image')

    cmd_convert = cmds.add_parser('convert', parents=[util.waitopts],
                                  help='Convert images to snapshots',
                                  description='Convert images to snapshots')
    cmd_convert.add_argument('-M', '--multiple', action='store_true',
                             help='Convert multiple images with the same name'
                                  ' instead of erroring')
    cmd_convert.add_argument('image', nargs='+',
                             help='ID, slug, or name of an image')

    util.add_actioncmds(cmds, 'image')

    args = parser.parse_args(argv, parsed)
    client, cache = util.mkclient(args)

    if args.cmd == 'show':
        if args.distribution:
            if args.image:
                util.die('--distribution and image arguments are mutually exclusive')
            util.dump(client.fetch_all_distribution_images())
        elif args.application:
            if args.image:
                util.die('--application and image arguments are mutually exclusive')
            util.dump(client.fetch_all_application_images())
        elif args.type:
            if args.image:
                util.die('--type and image arguments are mutually exclusive')
            util.dump(client.fetch_all_images(type=args.type))
        elif args.private:
            if args.image:
                util.die('--private and image arguments are mutually exclusive')
            util.dump(client.fetch_all_private_images())
        elif args.image:
            util.dump(cache.get_images(args.image, multiple=args.multiple,
                                                   hasM=True))
        else:
            util.dump(client.fetch_all_images())

    elif args.cmd == 'delete':
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        for i in imgs:
            i.delete()

    elif args.cmd == 'update':
        cache.check_name_dup("image", args.name, args.unique)
        img = cache.get_image(args.image, multiple=False)
        util.dump(img.update_image(args.name))

    elif args.cmd == 'transfer':
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        acts = (i.transfer(args.region) for i in imgs)
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd == 'convert':
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        acts = map(Image.convert, imgs)
        if args.wait:
            acts = client.wait_actions(acts)
        util.dump(acts)

    elif args.cmd in ('act', 'actions', 'wait'):
        imgs = cache.get_images(args.image, multiple=args.multiple, hasM=True)
        util.do_actioncmd(args, client, imgs)

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)


if __name__ == '__main__':
    main()
