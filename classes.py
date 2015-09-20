from urlparse import urljoin

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


class Action(JSObject):
    __slots__ = ()

    def __int__(self):
        return self.id

    @property
    def completed(self):
        return self.status == 'completed'

    @property
    def in_progress(self):
        return self.status == 'in-progress'

    @property
    def done(self):
        return self.status != 'in-progress'

    @property
    def errored(self):
        return self.status == 'errored'

    def url(self, endpoint=''):
        ### TODO: Look into the conditions under which this has to include the
        ### resource type & ID too
        return urljoin(endpoint, '/v2/actions/' + str(self.id))


class Droplet(JSObject):
    ### Should the `region` and `image` attributes be objects instead of dicts?

    __slots__ = ()

    def __int__(self):
        return self.id

    @property
    def active(self):
        return self.status == 'active'

    @property
    def new(self):
        return self.status == 'new'

    @property
    def off(self):
        return self.status == 'off'

    @property
    def archive(self):
        return self.status == 'archive'

    @property
    def region_slug(self):
        return self.region["slug"]

    @property
    def image_slug(self):
        return self.image["slug"]

    @property
    def ip_address(self):
        try:
            ### TODO: Are v4 and v6 both present right after a droplet is
            ### created?
            return (self.networks["v4"] + self.networks["v6"])[0]["ip_address"]
        except IndexError:
            return None

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/droplets/' + str(self.id))

    def action_url(self, endpoint=''):
        return urljoin(endpoint, '/v2/droplets/' + str(self.id) + '/actions')
