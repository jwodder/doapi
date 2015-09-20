#!/usr/bin/python
### Everything other than `request` returns only the actual relevant value,
### omitting `meta`, `links`, etc.  If you want the extra fields, do a raw
### request yourself.
import argparse
from   collections import defaultdict
import json
import os
from   time        import sleep, time
from   urlparse    import urljoin
import requests

class doapi(object):
    ENDPOINT = 'https://api.digitalocean.com'
    WAIT_INTERVAL = 10

    def __init__(self, api_key):
        ### Add things for config options
        ### Add an endpoint parameter?
        self.api_key = api_key
        self.timeout = 60
        self.endpoint = self.ENDPOINT

    def fullpath(self, path):
        return urljoin(self.endpoint, path)

    def request(self, url, params=None, method='GET'):
        if params is None:
            params = dict()
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json"
        }
        if method == 'GET':
            r = requests.get(url,
                             headers=headers,
                             params=params,
                             timeout=self.timeout)
        elif method == 'POST':
            r = requests.post(url,
                              headers=headers,
                              data=json.dumps(params),
                              timeout=self.timeout)
        elif method == 'PUT':
            r = requests.put(url,
                             headers=headers,
                             params=params,
                             timeout=self.timeout)
        elif method == 'DELETE':
            r = requests.delete(url, headers=headers, timeout=self.timeout)
        else:
            raise ValueError('Unrecognized HTTP method: ' + repr(method))
        if r.status_code != requests.codes.ok:
            ???
        elif method != 'DELETE':
            return r.json()

    def paginate(self, path, key, params=None):
        ### TODO: Handle `meta` and other extra fields
        data = []
        for page in self.raw_pages(path, params):
            data.extend(page[key])
        return data

    def raw_pages(self, path, params=None):
        url = self.fullpath(path)
        while True:
            r = self.request(url, params=params)
            yield r
            try:
                url = r["links"]["next"]
            except KeyError:
                break

    def all_droplets(self):
        return self.paginate('/v2/droplets', 'droplets')

    def get_droplet(self, id):
        return self.request('/v2/droplets/' + str(id))["droplet"]

    def get_action(self, id):
        ### THIS IS WRONG.
        return self.request('/v2/droplets/' + str(id))["action"]

    def droplet_upgrades(self):
        return self.request('/v2/droplet_upgrades')

    def create_droplet(self, name, image, size, region, **args):
        return self.request('/v2/droplets', method='POST', params={
            "name":               name,
            "image":              image,
            "size":               size,
            "region":             region,
            "ssh_keys":           args.get("ssh_keys", None),
            "backups":            args.get("backups", False),
            "ipv6":               args.get("ipv6", False),
            "private_networking": args.get("private_networking", False),
            "user_data":          args.get("user_data", None),
        })["droplet"]

    def wait_droplet_status(self, droplets, status="active", interval=None,
                            maxwait=-1):
        completed = []
        if interval is None:
            interval = self.WAIT_INTERVAL
        end_time = time() + maxwait if maxwait > 0 else None
        while droplets and (end_time is None or time() < end_time):
            next_droplets = []
            for d in droplets:
                d_id = d["id"] if isinstance(d, dict) else int(d)
                stats = self.get_droplet(d_id)
                if (stats["status"] == status if isinstance(status, basestring)
                                              else stats["status"] in status):
                    completed.append(stats)
                else:
                    next_droplets.append(stats)
            droplets = next_droplets
            if end_time is None:
                sleep(interval)
            else:
                sleep(min(interval, end_time - time()))
        return (completed, droplets)

    def wait_actions(self, actions, interval=None, maxwait=-1):
        completed = []
        errored = []
        if interval is None:
            interval = self.WAIT_INTERVAL
        end_time = time() + maxwait if maxwait > 0 else end_time = None
        while actions and (end_time is None or time() < end_time):
            next_actions = []
            for d in actions:
                d_id = d["id"] if isinstance(d, dict) else int(d)
                stats = self.get_action(d_id)
                if stats["status"] == "in-progress":
                    next_actions.append(stats)
                elif stats["status"] == "completed":
                    completed.append(stats)
                else:
                    errored.append(stats)
            actions = next_actions
            if end_time is None:
                sleep(interval)
            else:
                sleep(min(interval, end_time - time()))
        return (completed, errored, actions)

    def get_droplets_by_name(self, name):
        for page in self.raw_pages('/v2/droplets'):
            for drop in page["droplets"]:
                if drop["name"] == name:
                    yield drop

    def get_all_droplets_by_name(self):
        droplets = defaultdict(list)
        for page in self.raw_pages('/v2/droplets'):
            for drop in page["droplets"]:
                droplets[drop["name"]].append(drop)
        return droplets

    def get_ssh_key(self, id_or_print):
        return self.request('/v2/account/keys/' + str(id_or_print))["ssh_key"]
