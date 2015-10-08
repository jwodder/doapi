#!/usr/bin/python
import argparse
import os
import os.path
import sys
from   doapi import doapi, DOEncoder, byname

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

def do_droplet():
    parser = argparse.ArgumentParser(parents=[universal])
    cmds = parser.add_subparsers(title='command', dest='cmd')
    cmd_new = cmds.add_parser('new')
    ...
    args = parser.parse_args()
    client = mkclient(args)
    ...

def do_image():
    ...

def do_action():
    ...

def do_domain():
    ...

def do_sshkey():
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


def do_regions():
    parser = argparse.ArgumentParser(parents=[universal])
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_all_regions())

def do_sizes():
    parser = argparse.ArgumentParser(parents=[universal])
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_all_sizes())

def do_account():
    parser = argparse.ArgumentParser(parents=[universal])
    args = parser.parse_args()
    client = mkclient(args)
    dump(client.fetch_account())

def do_request():
    ...




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
            raise SystemExit('''\
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


def dump(obj):
    print json.dumps(obj, cls=DOEncoder, sort_keys=True, indent=4)


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
    if argv0 == 'do-droplet':
        do_droplet()
    elif argv0 == 'do-image':
        do_image()
    elif argv0 == 'do-action':
        do_action()
    elif argv0 == 'do-domain':
        do_domain()
    elif argv0 == 'do-sshkey':
        do_sshkey()
    elif argv0 == 'do-regions':
        do_regions()
    elif argv0 == 'do-sizes':
        do_sizes()
    elif argv0 == 'do-account':
        do_account()
    elif argv0 == 'do-request':
        do_request()
    else:
        raise SystemExit('''\
This command must be invoked as one of the following:
 - do-droplet
 - do-image
 - do-action
 - do-domain
 - do-sshkey
 - do-regions
 - do-sizes
 - do-account
 - do-request
''')
