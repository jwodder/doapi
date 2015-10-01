from   collections import defaultdict
import json
from   time        import sleep, time
from   urlparse    import urljoin
import requests
from   .base       import Region, Size, Account
from   .domain     import Domain
from   .droplet    import Droplet
from   .image      import Image
from   .action     import Action
from   .sshkey     import SSHKey

class doapi(object):
    def __init__(self, api_key, endpoint='https://api.digitalocean.com',
                 timeout=60, wait_interval=10, per_page=None):
        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout
        self.wait_interval = wait_interval
        self.per_page = per_page
        self.last_response = None
        self.last_meta = None

    def request(self, url, params={}, data={}, method='GET'):
        if url[:1] == "/":
            url = urljoin(self.endpoint, url)
        attrs = {
            "headers": {
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json"
            },
            "params": params,
            "timeout": self.timeout,
        }
        if method == 'GET':
            r = requests.get(url, **attrs)
        elif method == 'POST':
            r = requests.post(url, data=json.dumps(data), **attrs)
        elif method == 'PUT':
            r = requests.put(url, data=json.dumps(data), **attrs)
        elif method == 'DELETE':
            r = requests.delete(url, **attrs)
        else:
            raise ValueError('Unrecognized HTTP method: ' + repr(method))
        self.last_response = r
        self.last_meta = None
        r.raise_for_status()
        if method != 'DELETE':
            response = r.json()
            try:
                self.last_meta = response["meta"]
            except (KeyError, TypeError):
                pass
            return response

    @property
    def last_rate_limit(self):
        if self.last_response is None:
            return None
        else:
            ### Double-check this:
            return {k:v for k,v in self.last_response.headers.iteritems()
                        if k.startswith('ratelimit')}

    def paginate(self, path, key, params=None):
        if params is None:
            params = {}
        if self.per_page is not None:
            params["per_page"] = self.per_page
        while True:
            page = self.request(path, params=params)
            ### Could reusing `params` for non-first pages cause any problems?
            for obj in page[key]:
                yield obj
            try:
                path = page["links"]["pages"]["next"]
            except KeyError:
                break

    def droplet(self, obj):
        return Droplet(obj, doapi_manager=self)

    def fetch_droplet(self, obj):
        return self.droplet(obj).fetch()

    def fetch_all_droplets(self):
        return map(self.droplet, self.paginate('/v2/droplets', 'droplets'))

    def fetch_droplets_by_name(self, name):
        return [self.droplet(drop) for drop in self.paginate('/v2/droplets',
                                                             'droplets')
                                   if drop["name"] == name]

    def fetch_all_droplets_by_name(self):
        droplets = defaultdict(list)
        for drop in self.paginate('/v2/droplets', 'droplets'):
            droplets[drop["name"]].append(self.droplet(drop))
        return droplets

    def fetch_droplet_upgrades(self):
        return self.request('/v2/droplet_upgrades')

    def create_droplet(self, name, image, size, region, **data):
        # Standard optional attributes: ssh_keys, backups, ipv6,
        #     private_networking, user_data
        data["name"] = name
        data["image"] = image.id if isinstance(image, Image) else image
        data["size"] = str(size)
        data["region"] = str(region)
        try:
            keys = data["ssh_keys"]
        except KeyError:
            pass
        else:
            data["ssh_keys"] = [k.id_or_fingerprint if isinstance(k, SSHKey)
                                                    else k for k in keys]
        return self.droplet(self.request('/v2/droplets', method='POST',
                                         data=data)["droplet"])

    def fetch_droplet_neighbors(self):
        return [map(self.droplet, hood)
                for hood in self.paginate('/v2/reports/droplet_neighbors',
                                          'neighbors')]

    def wait_droplets(self, droplets, status=None, interval=None, maxwait=-1):
        droplets = map(self.droplet, droplets)
        if status is None:
            for a in self.wait_actions([d.fetch_last_action()
                                        for d in droplets],
                                       interval=interval, maxwait=maxwait):
                yield a.fetch_resource()
        else:
            if interval is None:
                interval = self.wait_interval
            end_time = time() + maxwait if maxwait > 0 else None
            while droplets and (end_time is None or time() < end_time):
                next_droplets = []
                for d in droplets:
                    drop = d.fetch()
                    if drop.status == status:
                        yield drop
                    else:
                        next_droplets.append(drop)
                droplets = next_droplets
                if end_time is None:
                    sleep(interval)
                else:
                    sleep(min(interval, end_time - time()))

    def action(self, obj):
        return Action(obj, doapi_manager=self)

    def fetch_action(self, obj):
        return self.action(obj).fetch()

    def fetch_last_action(self):
        ### Naive implementation:
        return self.action(self.request('/v2/actions')["actions"][0])
        """
        ### Slow yet guaranteed-correct implementation:
        return max(self.fetch_all_actions(), key=lambda a: a.started_at)
        """

    def fetch_all_actions(self):
        return map(self.action, self.paginate('/v2/actions', 'actions'))

    def wait_actions(self, actions, interval=None, maxwait=-1):
        actions = map(self.action, actions)
        if interval is None:
            interval = self.wait_interval
        end_time = time() + maxwait if maxwait > 0 else None
        while actions and (end_time is None or time() < end_time):
            next_actions = []
            for a in actions:
                act = a.fetch()
                if act.in_progress:
                    next_actions.append(act)
                else:
                    yield act
            actions = next_actions
            if end_time is None:
                sleep(interval)
            else:
                sleep(min(interval, end_time - time()))

    def sshkey(self, obj=None, **keyargs):
        return SSHKey(obj, doapi_manager=self, **keyargs)

    def fetch_sshkey(self, obj=None, **keyargs):
        return self.sshkey(obj, **keyargs).fetch()

    def fetch_all_sshkeys(self):
        return map(self.sshkey, self.paginate('/v2/account/keys', 'ssh_keys'))

    def create_sshkey(self, name, public_key):
        return self.sshkey(self.request('/v2/account/keys', method='POST', data={"name": name, "public_key": public_key})["ssh_key"])

    def image(self, obj):
        return Image(obj, doapi_manager=self)

    def fetch_image(self, obj):
        return self.image(obj).fetch()

    def fetch_all_images(self, type=None, private=False):
        params = {}
        if type is not None:
            params["type"] = type
        if private:
            params["private"] = 'true'
        return map(self.image, self.paginate('/v2/images', 'images',
                                             params=params))

    def fetch_all_distribution_images(self):
        return self.fetch_all_images(type='distribution')

    def fetch_all_application_images(self):
        return self.fetch_all_images(type='application')

    def fetch_all_private_images(self):
        return self.fetch_all_images(private=True)

    def region(self, obj):
        return Region(obj, doapi_manager=self)

    def fetch_all_regions(self):
        return map(self.region, self.paginate('/v2/regions', 'regions'))

    def size(self, obj):
        return Size(obj, doapi_manager=self)

    def fetch_all_sizes(self):
        return map(self.size, self.paginate('/v2/sizes', 'sizes'))

    def fetch_account(self):
        account = self.request(Account.url())["account"]
        account["doapi_manager"] = self
        return Account(account)

    def domain(self, obj):
        return Domain(obj, doapi_manager=self)

    def fetch_domain(self, obj):
        return self.domain(obj).fetch()

    def fetch_all_domains(self):
        return map(self.domain, self.paginate('/v2/domains', 'domains'))

    def create_domain(self, name, ip_address):
        return self.domain(self.request('/v2/domains', method='POST', data={
            "name": name,
            "ip_address": ip_address,
        })["domain"])

    ### fetch_droplet_upgrades
