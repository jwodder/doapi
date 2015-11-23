from .base import JSObjectWithID

class SSHKey(JSObjectWithID):
    """ TODO """

    def __init__(self, state=None, **extra):
        """ TODO """
        if isinstance(state, basestring):
            state = {"fingerprint": state}
        super(SSHKey, self).__init__(state, **extra)

    def __str__(self):
        return self.fingerprint

    @property
    def id_or_fingerprint(self):
        """
        The ``SSHKey``\ 's ``id`` field, or if that is not defined, its
        ``fingerprint`` field.  If neither field is defined, accessing this
        attribute raises a ``TypeError``.
        """
        if self.get("id") is not None:
            return self.id
        elif self.get("fingerprint") is not None:
            return self.fingerprint
        else:
            raise TypeError('SSHKey has neither .id nor .fingerprint')

    @property
    def url(self):
        """ The endpoint for operations on the specific SSH key """
        return self._url('/v2/account/keys/' + str(self.id_or_fingerprint))

    def fetch(self):
        """
        Fetch & return a new `SSHKey` object representing the SSH key's current
        state

        :rtype: SSHKey
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the SSH key no longer exists)
        """
        api = self.doapi_manager
        return api.ssh_key(api.request(self.url)["ssh_key"])

    def update_ssh_key(self, name):
        # The `_ssh_key` is to avoid conflicts with MutableMapping.update.
        """
        Update (i.e., rename) the SSH key

        :param str name: the new name for the SSH key
        :return: an updated `SSHKey` object
        :rtype: SSHKey
        """
        api = self.doapi_manager
        return api.ssh_key(api.request(self.url, method='PUT',
                                       data={"name": name})["ssh_key"])

    def delete(self):
        """
        Delete the SSH key

        :rtype: None
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')
