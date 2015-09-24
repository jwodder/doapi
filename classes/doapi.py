### Everything other than `request` returns only the actual relevant value,
### omitting `meta`, `links`, etc.  If you want the extra fields, do a raw
### request yourself.

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
        ### Add an endpoint parameter
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

    def droplet(self, obj):
        if isinstance(obj, (int, long)):
            dct = {"id": obj}
        elif isinstance(obj, Droplet):
            dct = obj._asdict()
        elif isinstance(obj, dict):
            dct = obj.copy()
        else:
            raise TypeError('argument must be integer, dict, or Droplet')
        dct["doapi_manager"] = self
        return Droplet(dct)

    def action(self, obj):
        if isinstance(obj, (int, long)):
            dct = {"id": obj}
        elif isinstance(obj, Action):
            dct = obj._asdict()
        elif isinstance(obj, dict):
            dct = obj.copy()
        else:
            raise TypeError('argument must be integer, dict, or Action')
        dct["doapi_manager"] = self
        return Action(dct)

    def all_droplets(self):
        return map(self.droplet, self.paginate('/v2/droplets', 'droplets'))

    def fetch_droplet(self, id):
        return self.droplet(self.request('/v2/droplets/%d' % (int(id),))["droplet"])

    def fetch_action(self, id):
        return self.action(self.request('/v2/droplets/%d' % (int(id),))["action"])

    def droplet_upgrades(self):
        return self.request('/v2/droplet_upgrades')

    def create_droplet(self, name, image, size, region, **args):
        return self.droplet(self.request('/v2/droplets', method='POST', params={
            "name":               name,
            "image":              image,
            "size":               size,
            "region":             region,
            "ssh_keys":           args.get("ssh_keys", None),
            "backups":            args.get("backups", False),
            "ipv6":               args.get("ipv6", False),
            "private_networking": args.get("private_networking", False),
            "user_data":          args.get("user_data", None),
        })["droplet"])

    def wait_droplets_status(self, droplets, status="active", interval=None,
                             maxwait=-1):
        completed = []
        if interval is None:
            interval = self.WAIT_INTERVAL
        end_time = time() + maxwait if maxwait > 0 else None
        while droplets and (end_time is None or time() < end_time):
            next_droplets = []
            for d in droplets:
                drop = self.fetch_droplet(d)
                if (drop.status == status if isinstance(status, basestring)
                                          else drop.status in status):
                    completed.append(drop)
                else:
                    next_droplets.append(drop)
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
            for a in actions:
                act = self.fetch_action(a)
                if act.in_progress:
                    next_actions.append(act)
                elif act.completed:
                    completed.append(act)
                else:
                    errored.append(act)
            actions = next_actions
            if end_time is None:
                sleep(interval)
            else:
                sleep(min(interval, end_time - time()))
        return (completed, errored, actions)

    def fetch_droplets_by_name(self, name):
        for page in self.raw_pages('/v2/droplets'):
            for drop in page["droplets"]:
                if drop["name"] == name:
                    yield self.droplet(drop)

    def fetch_all_droplets_by_name(self):
        droplets = defaultdict(list)
        for page in self.raw_pages('/v2/droplets'):
            for drop in page["droplets"]:
                droplets[drop["name"]].append(self.droplet(drop))
        return droplets

    def sshkey(self, obj=None, **keyargs):
        if obj is None:
            ### Do `dct = keyargs` instead?
            if keyargs.get("id", None) is not None:
                dct = {"id": keyargs["id"]}  ### Apply `int`?
            elif keyargs.get("fingerprint", None) is not None:
                dct = {"fingerprint": keyargs["fingerprint"]}  ### Apply `str`?
            else:
                raise TypeError('Neither "id" nor "fingerprint" is defined')
            """ ### Alternative:
            try:
                dct = {"id": keyargs["id"]}
            except KeyError:
                dct = {"fingerprint": keyargs["fingerprint"]}
            """
        elif isinstance(obj, (int, long)):
            dct = {"id": obj}
        elif isinstance(obj, basestring):
            dct = {"fingerprint": obj}
        elif isinstance(obj, SSHKey):
            dct = obj._asdict()
        elif isinstance(obj, dict):
            dct = obj.copy()
        else:
            raise TypeError('argument must be integer, string, dict, or SSHKey')
        dct["doapi_manager"] = self
        return SSHKey(dct)

    def fetch_sshkey(self, obj=None, **keyargs):
        return self.sshkey(obj, **keyargs).fetch()

    def all_sshkeys(self):
        return map(self.sshkey, self.paginate('/v2/account/keys', 'ssh_keys'))

    def create_sshkey(self, name, public_key):
        return self.sshkey(self.request('/v2/account/keys', method='POST', params={"name": name, "public_key": public_key})["ssh_key"])

    def image(self, obj):
        if isinstance(obj, (int, long)):
            dct = {"id": obj}
        elif isinstance(obj, Image):
            dct = obj._asdict()
        elif isinstance(obj, dict):
            dct = obj.copy()
        else:
            raise TypeError('argument must be integer, dict, or Image')
        dct["doapi_manager"] = self
        return Image(dct)

    def fetch_image(self, obj):
        return self.image(obj).fetch()

    def fetch_all_images(self, type=None, private=False):
        params = {}
        if type is not None:
            params["type"] = type
        if private:
            params["private"] = True
        return map(self.image, self.paginate('/v2/images', 'images',
                                             params=params)

    def fetch_all_distribution_images(self):
        return self.fetch_all_images(type='distribution')

    def fetch_all_application_images(self):
        return self.fetch_all_images(type='application')

    def fetch_all_private_images(self):
        return self.fetch_all_images(private=True)

    ### fetch_all_actions
    ### fetch_droplet_neighbors
    ### fetch_droplet_upgrades
