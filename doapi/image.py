from .base import Actionable, JSObjectWithDroplet, JSObjectWithID

class Image(Actionable, JSObjectWithDroplet, JSObjectWithID):
    # The `droplet` attribute is set for the "image" fields of droplets as well
    # as for the images returned by `Droplet.fetch_all_snapshots` and
    # `Droplet.fetch_all_backups`.

    def __str__(self):
        if self.get("slug") is not None:
            return self.slug
        else:
            raise AttributeError("%r object has no attribute 'slug'"
                                 % (self.__class__.__name__,))

    @property
    def url(self):
        return self._url('/v2/images/' + str(self.id))

    def fetch(self):
        api = self.doapi_manager
        return api.image(api.request(self.url)["image"])

    def update_image(self, name):
        # The `_image` is to avoid conflicts with MutableMapping.update.
        api = self.doapi_manager
        return api.image(api.request(self.url, method='PUT', data={"name": name})["image"])

    def delete(self):
        self.doapi_manager.request(self.url, method='DELETE')

    def transfer(self, region):
        return self.act(type='transfer', region=region)

    def convert(self):
        return self.act(type='convert')
