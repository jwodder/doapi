import json

# Don't use namedtuples for this or else everything will break if DigitalOcean
# ever adds any new fields.

class JSObject(object):
    def __init__(self, state={}, **extra):
        if isinstance(state, self.__class__):
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
        data.pop("doapi_manager", None)
        return data

    def __copy__(self):
        return self.__class__(vars(self))

    def __deepcopy__(self, memo):
        return self.__class__(deepcopy(vars(self), memo))


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


class Kernel(JSObject):
    def __int__(self):
        return self.id


class DropletUpgrade(JSObject):
    pass
