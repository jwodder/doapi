from   six   import string_types
from   .base import Actionable, Region, fromISO8601

class Volume(Actionable):
    """
    .. versionadded:: 0.3.0

    A block storage volume resource, representing data storage that can be
    added to a droplet and moved between droplets in the same region.

    New volumes are created via the :meth:`doapi.create_volume` method and can
    be retrieved with the :meth:`doapi.fetch_volume` and
    :meth:`doapi.fetch_all_volumes` methods.

    The DigitalOcean API specifies the following fields for volume objects:

    :var id: a unique identifier for the volume
    :vartype id: string

    :var created_at: date & time of the volume's creation
    :vartype created_at: datetime.datetime

    :var description: a human-readable free-form description for the volume
    :vartype description: string

    :var droplet_ids: IDs of droplets that the volume is currently attached to
    :vartype droplet_ids: list of integers

    :var name: a human-readable name for the volume
    :vartype name: string

    :var region: the region in which the volume is located
    :vartype region: `Region`

    :var size_gigabytes: the size of the volume in gigabytes
    :vartype size_gigabytes: integer
    """

    def __init__(self, state=None, **extra):
        if isinstance(state, string_types):
            state = {"id": state}
        super(Volume, self).__init__(state, **extra)
        for attr, cls in [('region', Region)]:
            if self.get(attr) is not None and not isinstance(self[attr], cls):
                self[attr] = cls(self[attr], doapi_manager=self.doapi_manager)
        self.created_at = fromISO8601(self.get('created_at'))

    def __str__(self):
        """ Convert the volume object to its ID """
        return self.id

    @property
    def url(self):
        """ The endpoint for general operations on the individual volume """
        return self._url('/v2/volumes/' + self.id)

    def fetch(self):
        """
        Fetch & return a new `Volume` object representing the volume's current
        state

        :rtype: Volume
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the volume no longer exists)
        """
        api = self.doapi_manager
        return api._volume(api.request(self.url)["volume"])

    def delete(self):
        """
        Delete the volume

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')

    def attach(self, droplet_id):
        """
        Attach the volume to a droplet

        :param droplet_id: the droplet to attach the volume to
        :type droplet_id: integer or `Droplet`
        :return: an `Action` representing the in-progress operation on the
            volume
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='attach', droplet_id=int(droplet_id))

    def detach(self, droplet_id):
        """
        Detach the volume from a droplet

        :param droplet_id: the droplet from which to remove the volume
        :type droplet_id: integer or `Droplet`
        :return: an `Action` representing the in-progress operation on the
            volume
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='detach', droplet_id=int(droplet_id))

    def resize(self, size_gigabytes):
        """
        Resize the volume

        :param size_gigabytes: the new size of the volume in gigabytes
        :type size_gigabytes: integer
        :return: an `Action` representing the in-progress operation on the
            volume
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='resize', size_gigabytes=size_gigabytes)
