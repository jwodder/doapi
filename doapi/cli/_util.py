import argparse
import os
import os.path
import sys
from   ..base  import DOEncoder
from   ..doapi import doapi

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


def mkclient(args):
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
    return (client, Cache(client))

def dump(obj, fp=sys.stdout):
    json.dump(obj, fp, cls=DOEncoder, sort_keys=True, indent=4)
    fp.write('\n')

def die(msg, *va_arg):
    raise SystemExit(sys.argv[0] + ': ' + msg % va_arg)

def byname(iterable):
    bins = defaultdict(list)
    for obj in iterable:
        bins[obj.name].append(obj)
    return bins
