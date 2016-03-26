from six   import string_types
from .base import ResourceWithID

class SSHKey(ResourceWithID):
    """
    An SSH key resource, representing an SSH public key that can be
    automatically added to the :file:`/root/.ssh/authorized_keys` files of new
    droplets.

    New SSH keys are created via the :meth:`doapi.create_ssh_key` method and
    can be retrieved with the :meth:`doapi.fetch_ssh_key` and
    :meth:`doapi.fetch_all_ssh_keys` methods.

    The DigitalOcean API specifies the following fields for SSH key objects:

    :var id: a unique identifier for the SSH key
    :vartype id: int

    :var fingerprint: the unique fingerprint of the SSH key
    :vartype fingerprint: string

    :var name: a human-readable name for the SSH key
    :vartype name: string

    :var public_key: the entire SSH public key as it was uploaded to
        DigitalOcean
    :vartype public_key: string
    """

    def __init__(self, state=None, **extra):
        if isinstance(state, string_types):
            state = {"fingerprint": state}
        super(SSHKey, self).__init__(state, **extra)

    def __str__(self):
        """ Convert the SSH key to its fingerprint """
        return self.fingerprint

    @property
    def _id(self):
        r"""
        The `SSHKey`'s ``id`` field, or if that is not defined, its
        ``fingerprint`` field.  If neither field is defined, accessing this
        attribute raises a `TypeError`.
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
        return self._url('/v2/account/keys/' + str(self._id))

    def fetch(self):
        """
        Fetch & return a new `SSHKey` object representing the SSH key's current
        state

        :rtype: SSHKey
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the SSH key no longer exists)
        """
        api = self.doapi_manager
        return api._ssh_key(api.request(self.url)["ssh_key"])

    def update_ssh_key(self, name):
        # The `_ssh_key` is to avoid conflicts with MutableMapping.update.
        """
        Update (i.e., rename) the SSH key

        :param str name: the new name for the SSH key
        :return: an updated `SSHKey` object
        :rtype: SSHKey
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return api._ssh_key(api.request(self.url, method='PUT',
                                       data={"name": name})["ssh_key"])

    def delete(self):
        """
        Delete the SSH key

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')
