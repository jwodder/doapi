from urlparse import urljoin
from .base    import JSObjectWithDroplet

class Image(JSObjectWithDroplet):
    # The `droplet` attribute is set when fetching a droplet's snapshots or
    # backups.

    def __int__(self):
        return self.id

    def __str__(self):
        if getattr(self, "slug", None) is not None:
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
        return api.image(api.request(self.url(), method='PUT',
                                     data={"name": name})["image"])

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')

    def act(self, **data):
        api = self.doapi_manager
        return api.action(api.request(self.action_url(), method='POST',
                                      data=data)["action"])

    def transfer(self, region):
        return self.act(type='transfer', region=region)

    def convert(self):
        return self.act(type='convert')

    def fetch_all_actions(self):
        api = self.doapi_manager
        return map(api.action, api.paginate(self.action_url(), 'actions'))

    def fetch_last_action(self):
        # Naive implementation:
        api = self.doapi_manager
        return api.action(api.request(self.action_url())["actions"][0])
        """
        # Slow yet guaranteed-correct implementation:
        return max(self.fetch_all_actions(), key=lambda a: a.started_at)
        """
