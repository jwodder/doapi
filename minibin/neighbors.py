#!/usr/bin/python
import os.path
import sys
sys.path.insert(1, sys.path[0] + '/..')
import doapi
from   tabulate import tabulate

fields = [
    ("ID", "id"),
    ("Name", "name"),
    ("IP address", "ip_address"),
    ("Status", "status"),
    ("Image", "image_slug"),
    ("Size", "size_slug"),
    ("Region", "region_slug"),
]

with open(os.path.expanduser('~/.doapi')) as fp:
    key = fp.read().strip()
api = doapi.doapi(key)

for dropid in sys.argv[1:]:
    drop = api.fetch_droplet(int(dropid))
    tabulate(zip(*fields)[0], [[getattr(act, f) for _, f in fields]
                               for act in drop.fetch_neighbors()])
    print
