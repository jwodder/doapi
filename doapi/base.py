import collections
import copy
import json
import numbers
from   urlparse  import urljoin
from   six       import iteritems
from   six.moves import map

class JSObject(collections.MutableMapping):
    _meta_attrs = ('data', 'doapi_manager')

    def __init__(self, state=None, **extra):
        # Note that meta attributes in `state` are not recognized as such, but
        # they are in `extra`.
        for attr in self._meta_attrs:
            self.__dict__[attr] = None
        self.data = {}
        if isinstance(state, self.__class__):
            for attr in self._meta_attrs:
                if attr != 'data':
                    setattr(self, attr, getattr(state, attr))
            state = state.data
        elif isinstance(state, JSObject):
            raise TypeError('%r object passed to %r constructor'
                            % (state.__class__.__name__,
                               self.__class__.__name__))
        if state is not None:
            self.data.update(state)
        for k,v in iteritems(extra):
            setattr(self, k, v)

    def __copy__(self):
        return self.__class__(self)

    def __deepcopy__(self, memo):
        dup = self.__class__()
        for attr in self._meta_attrs:
            setattr(self, attr, copy.deepcopy(getattr(self, attr), memo))
        return dup

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        # Meta attributes have to be omitted or else infinite recursion will
        # occur when trying to print a Droplet.
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join('%s=%r' % kv for kv in self.items()))

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError('%r object has no attribute %r'
                                 % (self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            self.data[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            del self.__dict__[name]
        else:
            del self.data[name]


class JSObjectWithID(JSObject):
    """
    A DigitalOcean API object with a unique integral ``id`` field.  Allows
    construction from an integer and implements ``__int__`` for conversion back
    to the integer.
    """

    def __init__(self, state=None, **extra):
        if isinstance(state, numbers.Integral):
            state = {"id": state}
        super(JSObjectWithID, self).__init__(state, **extra)

    def __int__(self):
        return self.id


class JSObjectWithDroplet(JSObject):
    """A JSObject with a "`droplet`" meta attribute"""

    _meta_attrs = JSObject._meta_attrs + ('droplet',)

    def fetch_droplet(self):
        if self.droplet is None:
            return None
        if self.doapi_manager is None:
            return self.droplet.fetch()
            # If `self.droplet` is an int, the user gets the AttributeError
            # they deserve.
        else:
            return self.doapi_manager.fetch_droplet(self.droplet)
            # If `self.droplet` is an int, the user doesn't get the
            # AttributeError they don't deserve.


class Actionable(JSObject):
    def action_url(self, endpoint=''):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def act(self, **data):
        api = self.doapi_manager
        return api.action(api.request(self.action_url(), method='POST',
                                      data=data)["action"])

    def wait(self, wait_interval=None, wait_time=None):
        list(self.doapi_manager.wait_actions([self.fetch_last_action()],
                                             wait_interval, wait_time))
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
            return obj.data
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


class Kernel(JSObjectWithDroplet, JSObjectWithID):
    pass


class DropletUpgrade(JSObject):
    def fetch_droplet(self):
        return self.doapi_manager.fetch_droplet(self.droplet_id)


class Networks(JSObjectWithDroplet):
    def __init__(self, state=None, **extra):
        super(Networks, self).__init__(state, **extra)
        meta = {
            "doapi_manager": self.doapi_manager,
            "droplet": self.droplet,
        }
        if self.get("v4"):
            self.v4 = [Network(obj, ip_version=4, **meta) for obj in self.v4]
        if self.get("v6"):
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
                for k,v in iteritems(body):
                    if not hasattr(self, k):
                        setattr(self, k, v)
