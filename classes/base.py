import json

# Don't use namedtuples for this or else everything will break if DigitalOcean
# ever adds any new fields.

# If I can do `droplet.region`, why not `droplet.region.slug`?  (That way lies
# pants on cats.)

class JSObject(object):
    def __init__(self, state):
        # This shadows properties/descriptors:
        self.__dict__.update(state)  # Does this not work in Python 3?
        # This does not (but will break if DO ever adds, say, a `completed`
        # field):
        #for k,v in state.iteritems():
        #    setattr(self, k, v)

    def _asdict(self):
        data = vars(self).copy()
        data.pop("doapi_manager", None)
        return data


class DOEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSObject):
            return obj._asdict()
        else:
            #return json.JSONEncoder.default(self, obj)
            return super(DOEncoder, self).default(obj)
