import argparse
import os
import os.path
from   string   import maketrans
import sys
from   .base    import DOEncoder, byname
from   .doapi   import doapi
from   .droplet import Droplet

universal = argparse.ArgumentParser(add_help=False)
keyopts = universal.add_mutually_exclusive_group()
keyopts.add_argument('--api-key')
keyopts.add_argument('--api-key-file', type=argparse.FileType('r'))
universal.add_argument('--timeout', type=float, metavar='seconds')
universal.add_argument('--endpoint')

waitbase = argparse.ArgumentParser(add_help=False)
waitbase.add_argument('--wait-time', type=float, metavar='seconds')
waitbase.add_argument('--wait-interval', type=float, metavar='seconds')

waitopts = argparse.ArgumentParser(parents=[waitbase], add_help=False)
waitopts.add_argument('--wait', action='store_true')

cache = None


unary_drop_acts = {under2hyphen(act): getattr(Droplet, act)
                   for act in "disable_backups reboot power_cycle shutdown"
                              " power_off power_on password_reset enable_ipv6"
                              " enable_private_networking upgrade".split()}

def doapi_droplet():
    parser = argparse.ArgumentParser(parents=[universal], prog='doapi-droplet')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('droplet', nargs='+')

    cmd_new = cmds.add_parser('new', parents=[waitopts])
    cmd_new.add_argument('-i', '--image', required=True)
    cmd_new.add_argument('-s', '--size', required=True)
    cmd_new.add_argument('-r', '--region', required=True)
    cmd_new.add_argument('--backups', action='store_true')
    cmd_new.add_argument('--ipv6', action='store_true')
    cmd_new.add_argument('-P', '--private-networking', action='store_true')
    cmd_new.add_argument('--user-data')
    ### --json
    ### ssh keys
    cmd_new.add_argument('name', nargs='+')

    cmd_wait = cmds.add_parser('wait', parents=[waitbase])
    cmd_wait.add_argument('-S', '--status', type=str.lower,
                          choices=['active', 'new', 'off', 'archive']
    cmd_wait.add_argument('droplet', nargs='+')

    for act in sorted(unary_drop_acts):
        cmds.add_parser(act, parents=[waitopts]).add_argument('droplet', nargs='+')

    for act in "snapshots backups kernels delete".split():
        cmds.add_parser(act).add_argument('droplet', nargs='+')

    cmd.add_parser('neighbors').add_argument('droplet', nargs='*')
    cmd.add_parser('upgrades').add_argument('--droplets', action='store_true')

    cmd_restore = cmds.add_parser('restore', parents=[waitopts])
    cmd_restore.add_argument('droplet')
    cmd_restore.add_argument('backup')

    cmd_resize = cmds.add_parser('resize', parents=[waitopts])
    cmd_resize.add_argument('--disk', action='store_true')
    cmd_resize.add_argument('droplet')
    cmd_resize.add_argument('size')

    cmd_rebuild = cmds.add_parser('rebuild', parents=[waitopts])
    cmd_rebuild.add_argument('--image')
    cmd_rebuild.add_argument('droplet', nargs='+')

    cmd_rename = cmds.add_parser('rename', parents=[waitopts])
    cmd_rename.add_argument('droplet')
    cmd_rename.add_argument('name')

    cmd_snapshot = cmds.add_parser('snapshot', parents=[waitopts])
    cmd_snapshot.add_argument('droplet')
    cmd_snapshot.add_argument('name')

    cmd_chkernel = cmds.add_parser('change-kernel', parents=[waitopts])
    cmd_chkernel.add_argument('droplet')
    cmd_chkernel.add_argument('kernel', type=int)

    ### raw action, getting actions/last action, etc.

    ...
    args = parser.parse_args()
    client = mkclient(args)
    if args.cmd == 'show':
        dump(cache.get_droplets(args.droplet, multiple=True))

    elif args.cmd == 'new':
        ...

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
        dump(acts)

    elif args.cmd == 'snapshots':
        dump(map(Droplet.fetch_all_snapshots,
                 cache.get_droplets(args.droplet, multiple=False)))
    elif args.cmd == 'backups':
        dump(map(Droplet.fetch_all_backups,
                 cache.get_droplets(args.droplet, multiple=False)))
    elif args.cmd == 'kernels':
        dump(map(Droplet.fetch_all_kernels,
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
        dump(act)

    elif args.cmd == 'resize':
        drop = cache.get_droplet(args.droplet, multiple=False)
        ### Check that `args.size` is an actual size?
        act = drop.resize(args.size, disk=args.disk)
        if args.wait:
            act = act.wait()
        dump(act)

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
        dump(acts)

    elif args.cmd == 'rename':
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.rename(args.name)
        if args.wait:
            act = act.wait()
        dump(act)

    elif args.cmd == 'snapshot':
        drop = cache.get_droplet(args.droplet, multiple=False)
        act = drop.snapshot(args.name)
        if args.wait:
            act = act.wait()
        dump(act)

    elif args.cmd == 'change-kernel':
        drop = cache.get_droplet(args.droplet, multiple=False)
        ### Check that `kernel` is actually a kernel?
        act = drop.change_kernel(args.kernel)
        if args.wait:
            act = act.wait()
        dump(act)

    else:
        assert False


def doapi_image():
    ...

def doapi_action():
    ...

def doapi_domain():
    ...

def doapi_sshkey():
    parser = argparse.ArgumentParser(parents=[universal], prog='doapi-sshkey')
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('sshkey', nargs='+')
    cmd_new = cmds.add_parser('new')
    cmd_new.add_argument('name')
    cmd_new.add_argument('pubkey', type=argparse.FileType('r'), nargs='?',
                         default=sys.stdin)
    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('sshkey', nargs='+')
    cmd_update = cmds.add_parser('update')
    cmd_update.add_argument('sshkey')
    cmd_update.add_argument('name')
    args = parser.parse_args()
    client = mkclient(args)
    if args.cmd == 'show':
        dump(cache.get_sshkeys(args.sshkey, multiple=True))
    elif args.cmd == 'new':
        dump(client.create_sshkey(args.name, args.pubkey.read().strip()))
    elif args.cmd == 'delete':
        keys = cache.get_sshkeys(args.sshkey, multiple=False)
        for k in keys:
            k.delete()
    elif args.cmd == 'update':
        key = cache.get_sshkey(args.sshkey, multiple=False)
        dump(key.update(args.name))
    else:
        assert False


def doapi_regions():
    parser = argparse.ArgumentParser(parents=[universal], prog='doapi-regions')
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_all_regions())

def doapi_sizes():
    parser = argparse.ArgumentParser(parents=[universal], prog='doapi-sizes')
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_all_sizes())

def doapi_account():
    parser = argparse.ArgumentParser(parents=[universal], prog='doapi-account')
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_account())

def doapi_request():
    ### DOC NOTE: --dump-header dumps as JSON, because it's much easier that
    ### way.
    parser = argparse.ArgumentParser(parents=[universal], prog='doapi-request')
    parser.add_argument('-X', '--request', type=str.upper, default='GET',
                        choices=['GET', 'POST', 'PUT', 'DELETE'])
    parser.add_argument('-d', '--data', metavar='string|@file')
    parser.add_argument('-D', '--dump-header', type=argparse.FileType('w'))
    parser.add_argument('--paginate', metavar='key')
    parser.add_argument('path', metavar='URL|path')
    args = parser.parse_args()
    if args.paginate is not None and args.request != 'GET':
        die('--paginate can only be used with the GET method')
    if args.data is not None:
        ### Complain if the request method is GET or DELETE?
        if len(args.data) > 1 and args.data[0] == '@':
            if args.data[1:] == '-':
                extra = {"data": sys.stdin.read()}
            else:
                with open(args.data[1:]) as fp:
                    extra = {"data": fp.read()}
        else:
            extra = {"data": args.data}
    else:
        extra = {}
    client = mkclient(args)
    if args.paginate is None:
        response = client.request(args.path, method=args.request, **extra)
    else:
        ### TODO: Print paginated results as they come in rather than all at
        ### once.
        response = list(client.paginate(args.path, args.paginate))
    if args.dump_header:
        # Using "with" would cause `args.dump_header` to close afterwards,
        # which would cause problems if it was stdout.  "with" technically
        # doesn't provide any benefit here anyway.
        dump(dict(client.last_response.headers), fp=args.dump_header)
    if args.request != 'DELETE':
        dump(response)


def mkclient(args):
    global cache
    if args.api_key is not None:
        api_key = args.api_key
    elif args.api_key_file is not None:
        with args.api_key_file as fp:
            api_key = fp.read().strip()
    elif "DO_API_KEY" in os.environ:
        api_key = os.environ["DO_API_KEY"]
    elif "DO_API_TOKEN" in os.environ"
        api_key = os.environ["DO_API_TOKEN"]
    else:
        try:
            with open(os.path.expanduser('~/.doapi')) as fp:
                api_key = fp.read().strip()
        except IOError:
            die('''\
No DigitalOcean API key supplied

Specify your API key via one of the following (in order of precedence):
 - the `--api-key KEY` or `--api-key-file FILE` option
 - the `DO_API_KEY` or `DO_API_TOKEN` environment variable
 - a ~/.doapi file
''')
    client = doapi(api_key, **{param: getattr(args, param)
                               for param in "timeout endpoint wait_interval"
                                            " wait_time".split()
                               if getattr(args, param, None) is not None})
    cache = Cache(client)
    return client


def dump(obj, fp=sys.stdout):
    json.dump(obj, fp, cls=DOEncoder, sort_keys=True, indent=4)
    fp.write('\n')


def die(msg, *va_arg):
    raise SystemExit(sys.argv[0] + ': ' + msg % va_arg)


us2h = maketrans('_', '-')

def under2hypen(s):
    return s.translate(us2h)


class Cache(object):
    ### TODO: When not all objects of a type have been fetched, labels that are
    ### valid IDs should not cause everything to be fetched (but the result
    ### should still be cached).

    groupby = {
        "droplet": ("id", "name"),
        "sshkey": ("id", "fingerprint", "name"),
        "image": ("id", "slug", "name"),
        ###"action": ("id",),
    }

    def __init__(self, client):
        self.client = client
        self.caches = {}

    def cache(self, objects, key):
        if key not in self.caches:
            grouped = {key: objects}
            for attr in self.groupby[key]:
                if attr == "name":
                    grouped[attr] = byname(objects)
                else:
                    grouped[attr] = {getattr(obj, attr): obj
                                     for obj in objects
                                     if getattr(obj, attr, None) is not None}
            self.caches[key] = grouped

    def get(self, key, label, multiple=True):
        grouped = self.caches[key]
        for attr in self.groupby[key]:
            if attr == "id":
                try:
                    idno = int(label)
                except ValueError:
                    continue
                else:
                    answer = grouped[attr].get(idno)
            else:
                answer = grouped[attr].get(label)
            if answer is not None:
                if attr == "name":
                    if multiple:
                        return answer
                    elif len(answer) == 1:
                        return answer[0]
                    else:
                        raise SystemError('%r: ambiguous; name used by'
                                          ' multiple %ss' % (label, key))
                elif multiple:
                    return [answer]
                else:
                    return answer
        raise SystemError('%r: no such %s' % (label, key))

    def cache_sshkeys(self):
        self.cache(self.client.fetch_all_sshkeys(), "sshkey")

    def get_sshkey(self, label, multiple=True):
        self.cache_sshkeys()
        self.get("sshkey", label, multiple)

    def get_sshkeys(self, labels, multiple=True):
        if multiple:
            return [key for l in labels for key in self.get_sshkey(l, True)]
        else:
            return [self.get_sshkey(l, False) for l in labels]

    def cache_droplets(self):
        self.cache(self.client.fetch_all_droplets(), "droplet")

    def get_droplet(self, label, multiple=True):
        self.cache_droplets()
        self.get("droplet", label, multiple)

    def get_droplets(self, labels, multiple=True):
        if multiple:
            return [drop for l in labels for drop in self.get_droplet(l, True)]
        else:
            return [self.get_droplet(l, False) for l in labels]

    def cache_images(self):
        self.cache(self.client.fetch_all_images(), "image")

    def get_image(self, label, multiple=True):
        self.cache_images()
        self.get("image", label, multiple)

    def get_images(self, labels, multiple=True):
        if multiple:
            return [img for l in labels for img in self.get_image(l, True)]
        else:
            return [self.get_image(l, False) for l in labels]


if __name__ == '__main__':
    argv0 = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if argv0 == 'doapi' and len(sys.argv) > 1:
        argv0 += '-' + sys.argv.pop(1)
    if argv0 == 'doapi-droplet':
        doapi_droplet()
    elif argv0 == 'doapi-image':
        doapi_image()
    elif argv0 == 'doapi-action':
        doapi_action()
    elif argv0 == 'doapi-domain':
        doapi_domain()
    elif argv0 == 'doapi-sshkey':
        doapi_sshkey()
    elif argv0 == 'doapi-regions':
        doapi_regions()
    elif argv0 == 'doapi-sizes':
        doapi_sizes()
    elif argv0 == 'doapi-account':
        doapi_account()
    elif argv0 == 'doapi-request':
        doapi_request()
    else:
        die('Available commands:\n'
            '    account action domain droplet image regions request sizes'
            ' sshkey')
