from urlparse import urljoin
from .base    import JSObjectWithID

class SSHKey(JSObjectWithID):
    def __init__(self, state=None, **extra):
        if isinstance(state, basestring):
            state = {"fingerprint": state}
        super(SSHKey, self).__init__(state, **extra)

    def __str__(self):
        return self.fingerprint

    @property
    def id_or_fingerprint(self):
        if self.get("id") is not None:
            return self.id
        elif self.get("fingerprint") is not None:
            return self.fingerprint
        else:
            raise TypeError('SSHKey has neither .id nor .fingerprint')

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/account/keys/'
                                 + str(self.id_or_fingerprint))

    def fetch(self):
        api = self.doapi_manager
        return api.sshkey(api.request(self.url())["ssh_key"])

    def update_sshkey(self, name):
        # The `_sshkey` is to avoid conflicts with MutableMapping.update.
        api = self.doapi_manager
        return api.sshkey(api.request(self.url(), method='PUT',
                                      data={"name": name})["ssh_key"])

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')
