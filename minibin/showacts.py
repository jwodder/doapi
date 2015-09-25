#!/usr/bin/python
import os.path
import sys
sys.path.insert(1, sys.path[0] + '/..')
import doapi
from   tabulate import tabulate

fields = [
    ("ID", "id"),
    ("Status", "status"),
    ("Type", "type"),
    ("Start", "started_at"),
    ("End", "completed_at"),
    ("Region", "region_slug"),
]

with open(os.path.expanduser('~/.doapi')) as fp:
    key = fp.read().strip()
api = doapi.doapi(key)
tabulate(zip(*fields)[0], [[getattr(drop, f) for _, f in fields]
                           for drop in api.fetch_all_actions()])
