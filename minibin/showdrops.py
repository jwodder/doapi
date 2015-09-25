#!/usr/bin/python
import os.path
import sys
sys.path.insert(1, sys.path[0] + '/..')
import doapi

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
values = []
for drop in api.fetch_all_droplets():
    values.append([getattr(drop, f) for _, f in fields])

lengths = [max(max(len(str(drop[i])) for drop in values), len(name))
           for i, (name, _) in enumerate(fields)]

print '|'.join('%-*s' % (sz, name) for (name, _), sz in zip(fields, lengths))
print '|'.join('-' * sz for sz in lengths)
for drop in values:
    print '|'.join('%-*s' % szval for szval in zip(lengths, drop))
