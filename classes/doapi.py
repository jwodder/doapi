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

    def droplet(self, obj):
        if isinstance(obj, (int, long)):
            dct = {"id": obj}
        elif isinstance(obj, dict):
            dct = obj.copy()
        elif isinstance(obj, Droplet):
            dct = obj._asdict()
        else:
            raise TypeError('argument must be integer, dict, or Droplet')
        dct["doapi_manager"] = self
        return Droplet(dct)

    def action(self, obj):
        if isinstance(obj, (int, long)):
            dct = {"id": obj}
        elif isinstance(obj, dict):
            dct = obj.copy()
        elif isinstance(obj, Action):
            dct = obj._asdict()
        else:
            raise TypeError('argument must be integer, dict, or Action')
        dct["doapi_manager"] = self
        return Action(dct)

    def all_droplets(self):
        return map(self.droplet, self.paginate('/v2/droplets', 'droplets'))

    def get_droplet(self, id):
        return self.droplet(self.request('/v2/droplets/%d' % (id,))["droplet"])

    def get_action(self, id):
        return self.action(self.request('/v2/droplets/%d' % (id,))["action"])

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

    def wait_droplet_status(self, droplets, status="active", interval=None,
                            maxwait=-1):
        completed = []
        if interval is None:
            interval = self.WAIT_INTERVAL
        end_time = time() + maxwait if maxwait > 0 else None
        while droplets and (end_time is None or time() < end_time):
            next_droplets = []
            for d in droplets:
                drop = self.get_droplet(d)
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
                act = self.get_action(a)
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

    def get_droplets_by_name(self, name):
        for page in self.raw_pages('/v2/droplets'):
            for drop in page["droplets"]:
                if drop["name"] == name:
                    yield self.droplet(drop)

    def get_all_droplets_by_name(self):
        droplets = defaultdict(list)
        for page in self.raw_pages('/v2/droplets'):
            for drop in page["droplets"]:
                droplets[drop["name"]].append(self.droplet(drop))
        return droplets

    def get_ssh_key(self, id_or_print):
        return self.request('/v2/account/keys/' + str(id_or_print))["ssh_key"]

    def droplet_action(self, drop, **params):
        return self.action(self.request('/v2/droplets/%d/actions' % (drop,),
                                        method='POST', params=params)["action"])

    def disable_backups(self, drop):
        return self.droplet_action(drop, type='disable_backups')

    def reboot(self, drop):
        return self.droplet_action(drop, type='reboot')

    def power_cycle(self, drop):
        return self.droplet_action(drop, type='power_cycle')

    def shutdown(self, drop):
        return self.droplet_action(drop, type='shutdown')

    def power_off(self, drop):
        return self.droplet_action(drop, type='power_off')

    def power_on(self, drop):
        return self.droplet_action(drop, type='power_on')

    def restore(self, drop, image):
        return self.droplet_action(drop, type='restore', image=image)

    def password_reset(self, drop):
        return self.droplet_action(drop, type='password_reset')

    def resize(self, drop, size, disk=None):
        opts = {"disk": disk} if disk is not None else {}
        return self.droplet_action(drop, type='resize', size=size, **opts)

    def rebuild(self, drop, image):
        return self.droplet_action(drop, type='rebuild', image=image)

    def rename(self, drop, name):
        return self.droplet_action(drop, type='rename', name=name)

    def change_kernel(self, drop, kernel):
        return self.droplet_action(drop, type='change_kernel', kernel=kernel)

    def enable_ipv6(self, drop):
        return self.droplet_action(drop, type='enable_ipv6')

    def enable_private_networking(self, drop):
        return self.droplet_action(drop, type='enable_private_networking')

    def snapshot(self, drop, name):
        return self.droplet_action(drop, type='snapshot', name=name)

    def upgrade(self, drop):
        return self.droplet_action(drop, type='upgrade')

    def delete_droplet(self, drop):
        self.request('/v2/droplets/%d' % (drop,), method='DELETE')

    def droplet_neighbors(self, drop):
        # Yes, that's really supposed to be a literal backslash in the URL.
        return map(self.droplet, self.paginate(r'/v2/droplets/%d\neighbors' % (drop,), 'droplets'))

    ### def wait_droplet  # wait for most recent action to complete/error
