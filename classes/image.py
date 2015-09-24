from urlparse import urljoin

class Image(JSObject):
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
        return api.image(api.request(self.url(), method='PUT')["image"])

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

    ### fetch_actions
