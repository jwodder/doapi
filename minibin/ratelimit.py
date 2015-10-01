#!/usr/bin/python
import json
import os.path
import sys
sys.path.insert(1, sys.path[0] + '/..')
import doapi

with open(os.path.expanduser('~/.doapi')) as fp:
    key = fp.read().strip()
api = doapi.doapi(key)
api.fetch_account()
print json.dumps(api.last_rate_limit, sort_keys=True, indent=4)
