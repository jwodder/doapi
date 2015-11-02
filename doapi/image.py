from urlparse import urljoin
from .base    import JSObjectWithDroplet, Actionable

class Image(JSObjectWithDroplet, Actionable):
    # The `droplet` attribute is set for the "image" fields of droplets as well
    # as for the images returned by `Droplet.fetch_all_snapshots` and
    # `Droplet.fetch_all_backups`.

    def __int__(self):
        return self.id

    def __str__(self):
        if self.get("slug") is not None:
            return self.slug
        else:
            raise AttributeError("%r object has no attribute 'slug'"
                                 % (self.__class__.__name__,))

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/images/' + str(self.id))

    def action_url(self, endpoint=''):
        return urljoin(endpoint, '/v2/images/' + str(self.id) + '/actions')

    def fetch(self):
        api = self.doapi_manager
        return api.image(api.request(self.url())["image"])

    def update(self, name):
        api = self.doapi_manager
        return api.image(api.request(self.url(), method='PUT', data={"name": name})["image"])

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')

    def transfer(self, region):
        return self.act(type='transfer', region=region)

    def convert(self):
        return self.act(type='convert')
