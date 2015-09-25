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
    "droplet":      api.fetch_all_droplets,
    "upgrade":      api.fetch_droplet_upgrades,
    "neighbor":     api.fetch_droplet_neighbors,
    "action":       api.fetch_all_actions,
    "image":        api.fetch_all_images,
    "distribution": api.fetch_all_distribution_images,
    "application":  api.fetch_all_application_images,
    "private":      api.fetch_all_private_images,
    "sshkey":       api.fetch_all_sshkeys,
    "region":       api.fetch_all_regions,
    "size":         api.fetch_all_sizes,
}

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(title='command', dest='cmd')
for rtype in fetchers:
    cmd = subparser.add_parser(rtype)
args = parser.parse_args()
print json.dumps(fetchers[args.cmd](), cls=doapi.DOEncoder,
                                       sort_keys=True,
                                       indent=4)
