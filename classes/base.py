# Don't use namedtuples for this or else everything will break if DigitalOcean
# ever adds any new fields.

class JSObject(dict):
    __slots__ = ()

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

# If I can do `droplet.region`, why not `droplet.region.slug`?  (That way lies
# pants on cats.)

#class JSObject(object):
#    def __init__(self, state):
#        # This shadows properties/descriptors:
#        self.__dict__.update(state)
#        # This does not (but will break if DO ever adds, say, a `completed`
#        # field):
#        #for k,v in state.iteritems():
#        #    setattr(self, k, v)
