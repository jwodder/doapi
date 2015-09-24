from urlparse import urljoin

class SSHKey(JSObject):
    def __int__(self):
        return self.id

    def url(self, endpoint=''):
        if getattr(self, 'id', None) is not None:
            base = self.id
        elif getattr(self, 'fingerprint', None) is not None:
            base = self.fingerprint
        else:
            raise TypeError('Neither .id nor .fingerprint is defined')
        return urljoin(endpoint, '/v2/account/keys/' + str(base))

    def fetch(self):
        api = self.doapi_manager
        return api.sshkey(api.request(self.url())["ssh_key"])

    def update(self, name):
        api = self.doapi_manager
        return api.sshkey(api.request(self.url(), method='PUT',
                                      data={"name": name})["ssh_key"])

    def destroy(self):  ### Rename "delete"?
        self.doapi_manager.request(self.url(), method='DELETE')
