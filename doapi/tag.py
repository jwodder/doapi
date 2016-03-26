from six          import iteritems, string_types
from .base        import Resource
from .droplet     import Droplet
from .floating_ip import FloatingIP
from .image       import Image

resource_types = {
    "droplets": Droplet,
    # Not supported by DO yet, but it's good to be prepared:
    "images": Image,
    "floating_ips": FloatingIP,
}

class Tag(Resource):
    """ TODO """

    def __init__(self, state=None, **extra):
        if isinstance(state, string_types):
            state = {"name": state}
        super(Tag, self).__init__(state, **extra)
        self.setdefault('resources', dict())
        for name, cls in iteritems(resource_types):
            if isinstance(self.resources.get(name), dict):
                last_tagged = self.resources[name].get("last_tagged")
                if last_tagged is not None and not isinstance(last_tagged, cls):
                    self.resources[name]["last_tagged"] = \
                        cls(last_tagged, doapi_manager=self.doapi_manager)

    @property
    def url(self):
        """ The endpoint for operations on the specific tag """
        return self._url('/v2/tags/' + self.name)

    def fetch(self):
        """
        Fetch & return a new `Tag` object representing the tag's current state

        :rtype: Tag
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the tag no longer exists)
        """
        api = self.doapi_manager
        return api._tag(api.request(self.url)["tag"])

    def __str__(self):
        """ Convert the tag object to its name """
        return self.name

    def update_tag(self, name):
        # The `_tag` is to avoid conflicts with MutableMapping.update.
        """
        Update (i.e., rename) the tag

        :param str name: the new name for the tag
        :return: an updated `Tag` object
        :rtype: Tag
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return api._tag(api.request(self.url, method='PUT',
                                    data={"name": name})["tag"])

    def delete(self):
        """
        Delete the tag

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')

    def add(self, *resources):
        self.doapi_manager.request(self.url + '/resources', method='POST',
                                   data={"resources": [r._taggable()
                                                       for r in resources]})

    def remove(self, *resources):
        self.doapi_manager.request(self.url + '/resources', method='DELETE',
                                   data={"resources": [r._taggable()
                                                       for r in resources]})
