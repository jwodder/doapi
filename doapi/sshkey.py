from urlparse import urljoin
from .base    import JSObject

class SSHKey(JSObject):
    def __init__(self, state={}, **extra):
        if isinstance(state, basestring):
            state = {"fingerprint": state}
        super(SSHKey, self).__init__(state, **extra)

    def __int__(self):
        return self.id

    @property
    def id_or_fingerprint(self):
        if getattr(self, 'id', None) is not None:
            return self.id
        elif getattr(self, 'fingerprint', None) is not None:
            return self.fingerprint
        else:
            raise TypeError('Neither .id nor .fingerprint is defined')

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/account/keys/'
                                 + str(self.id_or_fingerprint))

    def fetch(self):
        api = self.doapi_manager
        return api.sshkey(api.request(self.url())["ssh_key"])

    def update(self, name):
        api = self.doapi_manager
        return api.sshkey(api.request(self.url(), method='PUT',
                                      data={"name": name})["ssh_key"])

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')
