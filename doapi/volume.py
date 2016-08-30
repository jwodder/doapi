from   .base import Actionable, Region, fromISO8601

class Volume(Actionable):
    """ TODO """

    def __init__(self, state=None, **extra):
        super(Volume, self).__init__(state, **extra)
        for attr, cls in [('region', Region)]:
            if self.get(attr) is not None and not isinstance(self[attr], cls):
                self[attr] = cls(self[attr], doapi_manager=self.doapi_manager)
        self.droplet_ids = [
            self.doapi_manager._droplet(d) for d in self.get('droplet_ids', [])
        ]
        self.created_at = fromISO8601(self.get('created_at'))

    def __str__(self):
        """ TODO """
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

    def attach(self, droplet_id, region):
        """ TODO """
        ### Is `region` actually required?  Can't I just default it to
        ### `self.region.slug`?
        return self.act(
            type='attach',
            droplet_id=int(droplet_id),
            region=str(region),
        )

    def detach(self, droplet_id, region):
        """ TODO """
        ### Is `region` actually required?  Can't I just default it to
        ### `self.region.slug`?
        return self.act(
            type='detach',
            droplet_id=int(droplet_id),
            region=str(region),
        )

    def resize(self, size_gigabytes, region):
        """ TODO """
        ### Is `region` actually required?  Can't I just default it to
        ### `self.region.slug`?
        return self.act(
            type='resize',
            size_gigabytes=size_gigabytes,
            region=str(region),
        )
