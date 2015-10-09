from   collections import defaultdict
import json
from   time        import sleep, time
from   urlparse    import urljoin
import requests
from   .base       import Region, Size, Account, DropletUpgrade
from   .domain     import Domain
from   .droplet    import Droplet
from   .image      import Image
from   .action     import Action
from   .sshkey     import SSHKey

class doapi(object):
    def __init__(self, api_key, endpoint='https://api.digitalocean.com',
                 timeout=60, wait_interval=10, wait_time=None, per_page=None):
        # Note that timeout, wait_interval, and wait_time are a number of
        # seconds as an int or float.
        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout
        self.wait_interval = wait_interval
        self.wait_time = wait_time
        self.per_page = per_page
        self.last_response = None
        self.last_meta = None

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join('%s=%r' % kv
                                     for kv in vars(self).iteritems()))

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
        method = method.upper()
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
            return {k:v for k,v in self.last_response.headers.iteritems()
                        if k.startswith('ratelimit')}

    def paginate(self, path, key, params=None):
        if params is None:
            params = {}
        if self.per_page is not None:
            params["per_page"] = self.per_page
        page = self.request(path, params=params)
        while True:
            for obj in page[key]:
                yield obj
            try:
                url = page["links"]["pages"]["next"]
            except KeyError:
                break
            page = self.request(url)

    def droplet(self, obj):
        return Droplet(obj, doapi_manager=self)

    def fetch_droplet(self, obj):
        return self.droplet(obj).fetch()

    def fetch_all_droplets(self):
        return map(self.droplet, self.paginate('/v2/droplets', 'droplets'))

    def fetch_droplet_upgrades(self):
        return [DropletUpgrade(obj, doapi_manager=self)
                for obj in self.request('/v2/droplet_upgrades')]

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

    def wait_droplets(self, droplets, status=None, wait_interval=None,
                                                   wait_time=None):
        droplets = map(self.droplet, droplets)
        if status is None:
            for a in self.wait_actions([d.fetch_last_action()
                                        for d in droplets],
                                       wait_interval, wait_time)
                yield a.fetch_resource()
        else:
            return self._wait(droplets, lambda d: d.status == status,
                              wait_interval, wait_time)

    def action(self, obj):
        return Action(obj, doapi_manager=self)

    def fetch_action(self, obj):
        return self.action(obj).fetch()

    def fetch_last_action(self):
        # Naive implementation:
        return self.action(self.request('/v2/actions')["actions"][0])
        """
        # Slow yet guaranteed-correct implementation:
        return max(self.fetch_all_actions(), key=lambda a: a.started_at)
        """

    def fetch_all_actions(self):
        return map(self.action, self.paginate('/v2/actions', 'actions'))

    def wait_actions(self, actions, wait_interval=None, wait_time=None):
        return self._wait(map(self.action, actions), lambda a: a.done,
                          wait_interval, wait_time)

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

    def fetch_image_by_slug(self, slug):
        return self.image(self.request('/v2/images/' + slug)["image"])

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
        return Account(self.request(Account.url())["account"],
                       doapi_manager=self)

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

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def _wait(self, objects, isdone, wait_interval=None, wait_time=None)
        # `wait_time` can be set to a negative value to explicitly make the
        # function wait forever, overriding any positive value set for
        # `self.wait_time`
        objects = list(objects)
        if wait_interval is None:
            wait_interval = self.wait_interval
        if wait_time < 0:
            end_time = None
        else:
            if wait_time is None:
                wait_time = self.wait_time
            if wait_time is None or wait_time < 0:
                end_time = None
            else:
                end_time = time() + wait_time
        while objects and (end_time is None or time() < end_time):
            next_objs = []
            for o in objects:
                obj = o.fetch()
                if isdone(obj):
                    yield obj
                else:
                    next_objs.append(obj)
            objects = next_objs
            if end_time is None:
                sleep(wait_interval)
            else:
                sleep(min(wait_interval, end_time - time()))
        for o in objects:
            yield o
