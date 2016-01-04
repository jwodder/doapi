from .base import Actionable, ResourceWithDroplet, ResourceWithID

class Image(Actionable, ResourceWithDroplet, ResourceWithID):
    """
    TODO

    Note that calling a mutating method on an image does not cause the object
    to be updated; to get the most up to date information on an image, call
    the :meth:`fetch` method.

    Under normal circumstances, the "fetch" methods will only raise a
    `DOAPIError` if the image no longer exists.

    """

    # The `droplet` attribute is set for the "image" fields of droplets as well
    # as for the images returned by `Droplet.fetch_all_snapshots` and
    # `Droplet.fetch_all_backups`.

    def __str__(self):
        if self.get("slug") is not None:
            return self.slug
        else:
            raise AttributeError("%r object has no attribute 'slug'"
                                 % (self.__class__.__name__,))

    @property
    def url(self):
        """ The endpoint for operations on the specific image """
        return self._url('/v2/images/' + str(self.id))

    def fetch(self):
        """
        Fetch & return a new `Image` object representing the image's current
        state

        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the image no longer exists)
        """
        api = self.doapi_manager
        return api._image(api.request(self.url)["image"])

    def update_image(self, name):
        # The `_image` is to avoid conflicts with MutableMapping.update.
        """
        Update (i.e., rename) the image

        :param str name: the new name for the image
        :return: an updated `Image` object
        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return api._image(api.request(self.url, method='PUT',
                                               data={"name": name})["image"])

    def delete(self):
        """
        Delete the image

        :rtype: None
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')

    def transfer(self, region):
        """
        Transfer the image to another region

        :param region: the slug or `Region` object representing the region to
            which to transfer the image
        :type region: string or `Region`
        :return: an `Action` representing the in-progress operation on the
            image
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='transfer', region=region)

    def convert(self):
        """
        Convert the image to a snapshot

        :return: an `Action` representing the in-progress operation on the
            image
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='convert')
