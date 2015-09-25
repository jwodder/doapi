#!/usr/bin/python
import argparse
import json
import os.path
import sys
sys.path.insert(1, sys.path[0] + '/..')
import doapi

with open(os.path.expanduser('~/.doapi')) as fp:
    key = fp.read().strip()
api = doapi.doapi(key)

fetchers = {
    "droplet": api.fetch_droplet,
    "action":  api.fetch_action,
    "image":   api.fetch_image,
    "sshkey":  api.fetch_sshkey,
}

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(title='command', dest='cmd')
for rtype in fetchers:
    cmd = subparser.add_parser(rtype)
    cmd.add_argument('id', type=int)
args = parser.parse_args()
print json.dumps(fetchers[args.cmd](args.id), cls=doapi.DOEncoder,
                                              sort_keys=True,
                                              indent=4)
