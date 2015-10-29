import argparse
from   collections import defaultdict, Iterator
import json
import os
import os.path
import re
import sys
from   ..base      import DOEncoder
from   ..doapi     import doapi

universal = argparse.ArgumentParser(add_help=False)
tokenopts = universal.add_mutually_exclusive_group()
tokenopts.add_argument('--api-token')
tokenopts.add_argument('--api-token-file', type=argparse.FileType('r'))
universal.add_argument('--timeout', type=float, metavar='seconds')
universal.add_argument('--endpoint', metavar='URL')

waitbase = argparse.ArgumentParser(add_help=False)
waitbase.add_argument('--wait-time', type=float, metavar='seconds')
waitbase.add_argument('--wait-interval', type=float, metavar='seconds')

waitopts = argparse.ArgumentParser(parents=[waitbase], add_help=False)
waitopts.add_argument('--wait', action='store_true')


class Cache(object):
    ### TODO: When not all objects of a type have been fetched, labels that are
    ### valid IDs (or fingerprints or potential slugs) should not cause
    ### everything to be fetched (but the result should still be cached).

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

    def get(self, key, label, multiple=True, mandatory=True):
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
                        die('%r: ambiguous; name used by multiple %ss'
                            % (label, key))
                        ### Print the IDs of everything with that name?
                elif multiple:
                    return [answer]
                else:
                    return answer
        if mandatory:
            die('%r: no such %s' % (label, key))
        else:
            return [] if multiple else None

    def cache_sshkeys(self):
        self.cache(self.client.fetch_all_sshkeys(), "sshkey")

    def get_sshkey(self, label, multiple=True, mandatory=True):
        self.cache_sshkeys()
        return self.get("sshkey", label, multiple, mandatory)

    def get_sshkeys(self, labels, multiple=True):
        if multiple:
            return [key for l in labels for key in self.get_sshkey(l, True)]
        else:
            return [self.get_sshkey(l, False) for l in labels]

    def cache_droplets(self):
        self.cache(self.client.fetch_all_droplets(), "droplet")

    def get_droplet(self, label, multiple=True, mandatory=True):
        self.cache_droplets()
        return self.get("droplet", label, multiple, mandatory)

    def get_droplets(self, labels, multiple=True):
        if multiple:
            return [drop for l in labels for drop in self.get_droplet(l, True)]
        else:
            return [self.get_droplet(l, False) for l in labels]

    def cache_images(self):
        self.cache(self.client.fetch_all_images(), "image")

    def get_image(self, label, multiple=True, mandatory=True):
        self.cache_images()
        return self.get("image", label, multiple, mandatory)

    def get_images(self, labels, multiple=True):
        if multiple:
            return [img for l in labels for img in self.get_image(l, True)]
        else:
            return [self.get_image(l, False) for l in labels]


def mkclient(args):
    if args.api_token is not None:
        api_token = args.api_token
    elif args.api_token_file is not None:
        with args.api_token_file as fp:
            api_token = fp.read().strip()
    elif "DO_API_TOKEN" in os.environ:
        api_token = os.environ["DO_API_TOKEN"]
    else:
        try:
            with open(os.path.expanduser('~/.doapi')) as fp:
                api_token = fp.read().strip()
        except IOError:
            die('''\
No DigitalOcean API token supplied

Specify your API token via one of the following (in order of precedence):
 - the `--api-token TOKEN` or `--api-token-file FILE` option
 - the `DO_API_TOKEN` environment variable
 - a ~/.doapi file
''')
    client = doapi(api_token, **{param: getattr(args, param)
                                 for param in "timeout endpoint wait_interval"
                                              " wait_time".split()
                                 if getattr(args, param, None) is not None})
    return (client, Cache(client))

def dump(obj, fp=sys.stdout):
    if isinstance(obj, Iterator):
        fp.write('[\n')
        first = True
        for o in obj:
            if first:
                first = False
            else:
                fp.write(',\n')
            s = json.dumps(o, cls=DOEncoder, sort_keys=True, indent=4,
                           separators=(',', ': '))
            fp.write(re.sub(r'^', '    ', s, flags=re.M))
            fp.flush()
        fp.write('\n]\n')
    else:
        json.dump(obj, fp, cls=DOEncoder, sort_keys=True, indent=4,
                  separators=(',', ': '))
        fp.write('\n')

def die(msg, *va_arg):
    raise SystemExit(sys.argv[0] + ': ' + msg % va_arg)

def byname(iterable):
    bins = defaultdict(list)
    for obj in iterable:
        bins[obj.name].append(obj)
    return bins

def add_actioncmds(cmds, objtype):
    cmd_act = cmds.add_parser('act', parents=[waitbase])
    paramopts = cmd_act.add_mutually_exclusive_group()
    paramopts.add_argument('-p', '--params', metavar='JSON dict')
    paramopts.add_argument('-P', '--param-file', type=argparse.FileType('r'))
    cmd_act.add_argument('type')
    cmd_act.add_argument(objtype, nargs='+')
    cmd_actions = cmds.add_parser('actions')
    latestopts = cmd_actions.add_mutually_exclusive_group()
    latestopts.add_argument('--last', action='store_true')
    latestopts.add_argument('--in-progress', action='store_true')
    cmd_actions.add_argument(objtype, nargs='+')
    cmd_wait = cmds.add_parser('wait', parents=[waitbase])
    if objtype == 'droplet':
        cmd_wait.add_argument('-S', '--status', type=str.lower,
                              choices=['active', 'new', 'off', 'archive'])
    cmd_wait.add_argument(objtype, nargs='+')

def do_actioncmd(args, client, objects):
    if args.cmd == 'act':
        if args.params:
            params = json.loads(args.params)
            if not isinstance(params, dict):
                die('--params must be a JSON dictionary/object')
        elif args.param_file:
            with args.param_file:
                params = json.load(args.param_file)
            if not isinstance(params, dict):
                die('--param-file contents must be a JSON dictionary/object')
        else:
            params = {}
        actions = [obj.act(type=args.type, **params) for obj in objects]
        if args.wait:
            actions = client.wait_actions(actions)
        dump(actions)
    elif args.cmd == 'actions':
        if args.last or args.in_progress:
            actions = [obj.fetch_last_action() for obj in objects]
            if args.in_progress:
                actions = [a for a in actions if a.in_progress]
            dump(actions)
        else:
            dump([obj.fetch_all_actions() for obj in objects])
    elif args.cmd == 'wait':
        if getattr(args, "status", None) is not None:
            dump(client.wait_droplets(objects, status=args.status))
        else:
            actions = [obj.fetch_last_action() for obj in objects]
            dump(client.wait_actions(actions))
    else:
        raise RuntimeError('Programmer error: do_actioncmd called with invalid'
                           ' command')
