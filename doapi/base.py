import collections
import copy
import json
import numbers
from   urlparse  import urljoin
from   six.moves import map

class JSObject(object):
    # Don't use namedtuples for this or else everything will break if
    # DigitalOcean ever adds any new fields.

    _meta_attrs = ('_meta_attrs', 'doapi_manager')

    def __init__(self, state={}, **extra):
        if isinstance(state, numbers.Integral):
            state = {"id": state}
        elif isinstance(state, self.__class__):
            state = vars(state)
        # This shadows properties/descriptors:
        self.__dict__.update(state)
        self.__dict__.update(extra)
        # This does not (but will break if DO ever adds, say, a `completed`
        # field):
        """
        for k,v in state.iteritems():
            setattr(self, k, v)
        for k,v in extra.iteritems():
            setattr(self, k, v)
        """

    def _asdict(self):
        data = vars(self).copy()
        for attr in self._meta_attrs:
            data.pop(attr, None)
        return data

    def __copy__(self):
        return self.__class__(vars(self))

    def __deepcopy__(self, memo):
        return self.__class__(copy.deepcopy(vars(self), memo))

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        # Meta attributes have to be omitted or else infinite recursion will
        # occur when trying to print a Droplet.
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join('%s=%r' % kv
                                     for kv in self._asdict().iteritems()))


class JSObjectWithDroplet(JSObject):
    """A JSObject with a "`droplet`" meta attribute"""

    _meta_attrs = JSObject._meta_attrs + ('droplet',)

    def fetch_droplet(self):
        drop = getattr(self, "droplet", None)
        if drop is None:
            return None
        try:
            api = self.doapi_manager
        except AttributeError:
            return drop.fetch()
            # If `drop` is an int, the user gets the AttributeError they
            # deserve.
        else:
            return api.fetch_droplet(drop)
            # If `drop` is an int, the user doesn't get the AttributeError they
            # don't deserve.


class Actionable(JSObject):
    # abstract method: action_url (and fetch)

    def act(self, **data):
        api = self.doapi_manager
        return api.action(api.request(self.action_url(), method='POST',
                                      data=data)["action"])

    def wait(self, wait_interval=None, wait_time=None):
        list(self.doapi_manager.wait_actions([self.fetch_last_action()],
                                             status, wait_interval, wait_time))
        return self.fetch()

    def fetch_all_actions(self):
        api = self.doapi_manager
        return map(api.action, api.paginate(self.action_url(), 'actions'))

    def fetch_last_action(self):
        # Naive implementation:
        api = self.doapi_manager
        return api.action(api.request(self.action_url())["actions"][0])
        # Slow yet guaranteed-correct implementation:
        #return max(self.fetch_all_actions(), key=lambda a: a.started_at)


class DOEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSObject):
            return obj._asdict()
        elif isinstance(obj, collections.Iterator):
            return list(obj)
        else:
            #return json.JSONEncoder.default(self, obj)
            return super(DOEncoder, self).default(obj)


class Region(JSObject):
    def __str__(self):
        return self.slug


class Size(JSObject):
    def __str__(self):
        return self.slug


class Account(JSObject):
    def fetch(self):
        return self.doapi_manager.fetch_account()

    @staticmethod
    def url(endpoint=''):
        return urljoin(endpoint, '/v2/account')


class Kernel(JSObjectWithDroplet):
    def __int__(self):
        return self.id


class DropletUpgrade(JSObject):
    def fetch_droplet(self):
        return self.doapi_manager.fetch_droplet(self.droplet_id)


class Networks(JSObjectWithDroplet):
    def __init__(self, state={}, **extra):
        super(Networks, self).__init__(state, **extra)
        meta = {}
        for attr in ('doapi_manager', 'droplet'):
            if getattr(self, attr, None) is not None:
                meta[attr] = getattr(self, attr)
        if getattr(self, "v4", None):
            self.v4 = [Network(obj, ip_version=4, **meta) for obj in self.v4]
        if getattr(self, "v6", None):
            self.v6 = [Network(obj, ip_version=6, **meta) for obj in self.v6]


class Network(JSObjectWithDroplet):
    _meta_attrs = JSObjectWithDroplet._meta_attrs + ('ip_version',)

    def __str__(self):
        return self.ip_address


class DOAPIError(Exception):
    # Note that this class is only for representing errors reported by the
    # endpoint in response to API requests.  Everything else that can go wrong
    # uses the normal Python exceptions.
    def __init__(self, response):
        self.response = response
        # Taken from requests' raise_for_status:
        self.http_error_msg = ''
        if 400 <= response.status_code < 500:
            self.http_error_msg = '%s Client Error: %s for url: %s\n' \
                                  % (response.status_code, response.reason,
                                     response.url)
        elif 500 <= response.status_code < 600:
            self.http_error_msg = '%s Server Error: %s for url: %s\n' \
                                  % (response.status_code, response.reason,
                                     response.url)
        self.http_error_msg += response.text
        super(DOAPIError, self).__init__(self.http_error_msg)
        try:
            body = response.json()
        except ValueError:
            pass
        else:
            if isinstance(body, dict):
                for k,v in body.iteritems():
                    if not hasattr(self, k):
                        setattr(self, k, v)
