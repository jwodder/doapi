import argparse
from   collections import defaultdict, Iterator
import json
import os
import os.path
import re
import sys
from   ..          import __version__
from   ..base      import DOEncoder
from   ..doapi     import doapi

universal = argparse.ArgumentParser(add_help=False)
tokenopts = universal.add_mutually_exclusive_group()
tokenopts.add_argument('--api-token', metavar='TOKEN',
                       help='DigitalOcean API token')
tokenopts.add_argument('--api-token-file', type=argparse.FileType('r'),
                       metavar='FILE',
                       help='file containing DigitalOcean API token')
universal.add_argument('--timeout', type=float, metavar='SECONDS',
                       help='HTTP request timeout')
universal.add_argument('--endpoint', metavar='URL',
                       help='where to make API requests')
universal.add_argument('-V', '--version', action='version',
                                          version='doapi ' + __version__)

waitbase = argparse.ArgumentParser(add_help=False)
waitbase.add_argument('--wait-time', type=float, metavar='SECONDS',
                      help='maximum length of time to wait')
waitbase.add_argument('--wait-interval', type=float, metavar='SECONDS',
                      help='how often to check progress')

waitopts = argparse.ArgumentParser(parents=[waitbase], add_help=False)
waitopts.add_argument('--wait', action='store_true',
                      help='Wait for the operation to finish')


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
            objects = list(objects)
            grouped = {key: objects}
            for attr in self.groupby[key]:
                grouped[attr] = defaultdict(list)
                for obj in objects:
                    if obj.get(attr) is not None:
                        grouped[attr][obj[attr]].append(obj)
            self.caches[key] = grouped

    def get(self, key, label, multiple=True, mandatory=True, hasM=False):
        grouped = self.caches[key]
        for attr in self.groupby[key]:
            if attr == "id":
                try:
                    idno = int(label)
                except ValueError:
                    continue
                else:
                    answer = grouped[attr][idno]
            else:
                answer = grouped[attr][label]
            if answer:
                if multiple:
                    return answer
                elif len(answer) == 1:
                    return answer[0]
                else:
                    msg = '{0!r}: ambiguous; name used by multiple {1}s: {2}'.format(label, key, ', '.join(str(o.id) for o in answer))
                    if hasM:
                        msg += '\nUse the -M/--multiple option to specify' \
                               ' all of them at once.'
                    die(msg)
        if mandatory:
            die('{0!r}: no such {1}'.format(label, key))
        else:
            return [] if multiple else None

    def cache_sshkeys(self):
        self.cache(self.client.fetch_all_ssh_keys(), "sshkey")

    def get_sshkey(self, label, multiple=True, mandatory=True, hasM=False):
        self.cache_sshkeys()
        return self.get("sshkey", label, multiple, mandatory, hasM)

    def get_sshkeys(self, labels, multiple=True, hasM=False):
        if multiple:
            objs = [key for l in labels for key in self.get_sshkey(l, True)]
        else:
            objs = [self.get_sshkey(l, False, hasM=hasM) for l in labels]
        return rmdups(objs, 'SSH key')

    def add_sshkey(self, key):
        cache = self.caches["sshkey"]
        for attr in self.groupby["sshkey"]:
            value = key.get(attr)
            if value is not None:
                cache[attr][value].append(key)

    def cache_droplets(self):
        self.cache(self.client.fetch_all_droplets(), "droplet")

    def get_droplet(self, label, multiple=True, mandatory=True, hasM=False):
        self.cache_droplets()
        return self.get("droplet", label, multiple, mandatory, hasM)

    def get_droplets(self, labels, multiple=True, hasM=False):
        if multiple:
            objs = [drop for l in labels for drop in self.get_droplet(l, True)]
        else:
            objs = [self.get_droplet(l, False, hasM=hasM) for l in labels]
        return rmdups(objs, 'droplet')

    def cache_images(self):
        self.cache(self.client.fetch_all_images(), "image")

    def get_image(self, label, multiple=True, mandatory=True, hasM=False):
        self.cache_images()
        return self.get("image", label, multiple, mandatory, hasM)

    def get_images(self, labels, multiple=True, hasM=False):
        if multiple:
            objs = [img for l in labels for img in self.get_image(l, True)]
        else:
            objs = [self.get_image(l, False, hasM=hasM) for l in labels]
        return rmdups(objs, 'image')

    def check_name_dup(self, key, name, fatal):
        if key == "sshkey":
            self.cache_sshkeys()
        elif key == "droplet":
            self.cache_droplets()
        elif key == "image":
            self.cache_images()
        if name in self.caches[key]["name"] or \
                (key == "image" and name in self.caches[key]["slug"]):
            msg = 'There is already another {0} named {1!r}'.format(key, name)
            if fatal:
                die(msg)
            else:
                sys.stderr.write('Warning: ' + msg + '\n')


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
        fp.write('[')
        first = True
        for o in obj:
            if first:
                fp.write('\n')
                first = False
            else:
                fp.write(',\n')
            s = json.dumps(o, cls=DOEncoder, sort_keys=True, indent=4,
                           separators=(',', ': '))
            fp.write(re.sub(r'^', '    ', s, flags=re.M))
            fp.flush()
        if not first:
            fp.write('\n')
        fp.write(']\n')
    else:
        json.dump(obj, fp, cls=DOEncoder, sort_keys=True, indent=4,
                  separators=(',', ': '))
        fp.write('\n')

def die(msg):
    raise SystemExit(sys.argv[0] + ': ' + msg)

def currentActions(objs, withnulls=False):
    for o in objs:
        act = o.fetch_current_action()
        if act:
            yield act
        elif withnulls:
            yield None

def add_actioncmds(cmds, objtype, multiple=True):
    cmd_act = cmds.add_parser('act', parents=[waitopts],
                              help='Perform an arbitrary action',
                              description='Perform an arbitrary action')
    cmd_act.add_argument('-p', '--params', metavar='JSON|@file',
                         type=str_or_file,
                         help='JSON object of action arguments')
    if multiple:
        cmd_act.add_argument('-M', '--multiple', action='store_true',
                             help='Act on multiple resources with the same name'
                                  ' instead of erroring')
    cmd_act.add_argument('type', help='type of action to perform')
    cmd_act.add_argument(objtype, nargs='+',
                         help='identifier for a resource to act on')

    cmd_actions = cmds.add_parser('actions',
                                  help='List actions performed on resources',
                                  description='List actions performed on'
                                              ' resources')
    latestopts = cmd_actions.add_mutually_exclusive_group()
    latestopts.add_argument('--last', action='store_true',
                            help='Show only the most recent action on each'
                                 ' resource')
    latestopts.add_argument('--in-progress', action='store_true',
                            help='Show only in-progress actions')
    if multiple:
        cmd_actions.add_argument('-M', '--multiple', action='store_true',
                                 help='Act on multiple resources with the same'
                                      ' name instead of erroring')
    cmd_actions.add_argument(objtype, nargs='+',
                             help='identifier for a resource to fetch data for')

    cmd_wait = cmds.add_parser('wait', parents=[waitbase],
                               help="Wait for resources' most recent actions"
                                    " to complete",
                               description="Wait for resources' most recent"
                                           " actions to complete")
    if objtype == 'droplet':
        cmd_wait.add_argument('-S', '--status', type=str.lower,
                              choices=['active', 'new', 'off', 'archive'],
                              help="Wait for the droplets' statuses to reach"
                                   " the given value instead")
    if multiple:
        cmd_wait.add_argument('-M', '--multiple', action='store_true',
                              help='Act on multiple resources with the same'
                                   ' name instead of erroring')
    cmd_wait.add_argument(objtype, nargs='+',
                          help='identifier for a resource to wait on')

def do_actioncmd(args, client, objects):
    if args.cmd == 'act':
        if args.params is not None:
            params = json.loads(args.params)
            if not isinstance(params, dict):
                die('--params must be a JSON dictionary/object')
        else:
            params = {}
        actions = [obj.act(type=args.type, **params) for obj in objects]
        if args.wait:
            actions = client.wait_actions(actions)
        dump(actions)
    elif args.cmd == 'actions':
        if args.last or args.in_progress:
            if args.in_progress:
                actions = list(currentActions(objects, withnulls=True))
            else:
                actions = [obj.fetch_last_action() for obj in objects]
            dump(actions)
        else:
            dump(obj.fetch_all_actions() for obj in objects)
    elif args.cmd == 'wait':
        if getattr(args, "status", None) is not None:
            dump(client.wait_droplets(objects, status=args.status))
        else:
            actions = list(currentActions(objects))
            dump(client.wait_actions(actions))
    else:
        assert False, 'do_actioncmd called with invalid command'

def str_or_file(arg):
    if arg.startswith("@") and len(arg) > 1:
        if arg[1:] == '-':
            return sys.stdin.read()
        else:
            with open(arg[1:]) as fp:
                return fp.read()
    else:
        return arg

def rmdups(objs, objtype, idfield='id'):
    ### TODO: Rethink whether this should return a list or a generator (Would I
    ### want a generator for any non-showing operation?)
    seen = set()
    uniq = []
    for o in objs:
        idval = o[idfield]
        if idval in seen:
            sys.stderr.write('Warning: {0} {1!r} specified multiple times; ignoring later occurrence\n'.format(objtype, idval))
        else:
            seen.add(idval)
            uniq.append(o)
    return uniq
