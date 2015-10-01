import copy
import json
from   urlparse import urljoin

class JSObject(object):
    # Don't use namedtuples for this or else everything will break if
    # DigitalOcean ever adds any new fields.

    _meta_attrs = ('doapi_manager',)

    def __init__(self, state={}, **extra):
        if isinstance(state, (int, long)):
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


class DOEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSObject):
            return obj._asdict()
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


class Kernel(JSObject):
    _meta_attrs = JSObject._meta_attrs + ('droplet',)

    def __int__(self):
        return self.id

    def fetch_droplet(self):
        ### Handle self.droplet being an int?
        return self.droplet.fetch()


class DropletUpgrade(JSObject):
    def fetch_droplet(self):
        return self.doapi_manager.fetch_droplet(self.droplet_id)


def byname(iterable):
    bins = defaultdict(list)
    for obj in iterable:
        bins[obj.name].append(obj)
    return bins

def filterName(name, iterable):
    return [obj for obj in iterable if obj.name == name]
    """
    for obj in iterable:
        if obj.name == name:
            yield obj
    """
