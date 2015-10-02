from urlparse import urljoin
from .base    import JSObjectWithDroplet

class Image(JSObjectWithDroplet):
    # The `droplet` attribute is set when fetching a droplet's snapshots or
    # backups.

    def __int__(self):
        return self.id

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

    def action(self, **data):  ### TODO: Rethink name; `act`?
        api = self.doapi_manager
        return api.action(api.request(self.action_url(), method='POST',
                                      data=data)["action"])

    def transfer(self, region):
        return self.action(type='transfer', region=region)

    def convert(self):
        return self.action(type='convert')

    def fetch_all_actions(self):
        api = self.doapi_manager
        return map(api.action, api.paginate(self.action_url(), 'actions'))

    def fetch_last_action(self):
        ### Naive implementation:
        api = self.doapi_manager
        return api.action(api.request(self.action_url())["actions"][0])
        """
        ### Slow yet guaranteed-correct implementation:
        return max(self.fetch_all_actions(), key=lambda a: a.started_at)
        """
