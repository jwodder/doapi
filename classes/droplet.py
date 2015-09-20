from urlparse import urljoin

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
