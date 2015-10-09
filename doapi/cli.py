import argparse
import os
import os.path
import sys
from   .base  import DOEncoder, byname
from   .doapi import doapi

universal = argparse.ArgumentParser(add_help=False)
keyopts = universal.add_mutually_exclusive_group()
keyopts.add_argument('--api-key')
keyopts.add_argument('--api-key-file', type=argparse.FileType('r'))
universal.add_argument('--timeout', type=float, metavar='seconds')
universal.add_argument('--endpoint')

waitopts = argparse.ArgumentParser(add_help=False)
waitopts.add_argument('--wait', action='store_true')
waitopts.add_argument('--wait-time', type=float, metavar='seconds')
waitopts.add_argument('--wait-interval', type=float, metavar='seconds')

cache = None

def doapi_droplet():
    parser = argparse.ArgumentParser(parents=[universal])
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_new = cmds.add_parser('new')
    ...
    args = parser.parse_args()
    client = mkclient(args)
    ...

def doapi_image():
    ...

def doapi_action():
    ...

def doapi_domain():
    ...

def doapi_sshkey():
    parser = argparse.ArgumentParser(parents=[universal])
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('sshkeys', nargs='+')
    cmd_new = cmds.add_parser('new')
    cmd_new.add_argument('name')
    cmd_new.add_argument('pubkey', type=argparse.FileType('r'), nargs='?',
                         default=sys.stdin)
    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('sshkeys', nargs='+')
    cmd_update = cmds.add_parser('update')
    cmd_update.add_argument('sshkey')
    cmd_update.add_argument('name')
    args = parser.parse_args()
    client = mkclient(args)
    if args.cmd == 'show':
        dump([key for label in args.sshkeys
                  for key in cache.get_sshkey(label, multiple=True)])
    elif args.cmd == 'new':
        dump(client.create_sshkey(args.name, args.pubkey.read().strip()))
    elif args.cmd == 'delete':
        for label in args.sshkeys:
            for key in cache.get_sshkey(label, multiple=True):
                key.delete()
    elif args.cmd == 'update':
        key = cache.get_sshkey(args.sshkey, multiple=False)
        dump(key.update(args.name))
    else:
        assert False


def doapi_regions():
    parser = argparse.ArgumentParser(parents=[universal])
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_all_regions())

def doapi_sizes():
    parser = argparse.ArgumentParser(parents=[universal])
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_all_sizes())

def doapi_account():
    parser = argparse.ArgumentParser(parents=[universal])
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_account())

def doapi_request():
    ### DOC NOTE: --dump-header dumps as JSON, because it's much easier that
    ### way.
    parser = argparse.ArgumentParser(parents=[universal])
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
                    pass
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

    def cache_droplets(self):
        self.cache(self.client.fetch_all_droplets(), "droplet")

    def get_droplet(self, label, multiple=True):
        self.cache_droplets()
        self.get("droplet", label, multiple)

    def cache_images(self):
        self.cache(self.client.fetch_all_images(), "image")

    def get_image(self, label, multiple=True):
        self.cache_images()
        self.get("image", label, multiple)


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
