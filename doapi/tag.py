from six          import iteritems, string_types
from six.moves    import map  # pylint: disable=redefined-builtin
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
    r"""
    A tag resource, representing a label that can be applied to other
    resources.

    New tags are created via the :meth:`doapi.create_tag` method and can be
    retrieved with the :meth:`doapi.fetch_tag` and :meth:`doapi.fetch_all_tags`
    methods.

    The DigitalOcean API specifies the following fields for tag objects:

    :var name: the name of the tag
    :vartype name: string

    :var resources: a `dict` mapping resource types (e.g., ``"droplets"``) to
        sub-`dict`\ s containing fields ``"count"`` (the number of resources of
        the given type with the given tag) and ``"last_tagged"`` (the resource
        of the given type to which the tag was most recently applied)
    """

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
        """ The endpoint for general operations on the individual tag """
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
        """
        Apply the tag to one or more resources

        :param resources: one or more `Resource` objects to which tags can be
            applied
        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url + '/resources', method='POST',
                                   data={"resources": _to_taggable(resources)})

    def remove(self, *resources):
        """
        Remove the tag from one or more resources

        :param resources: one or more `Resource` objects to which tags can be
            applied
        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url + '/resources', method='DELETE',
                                   data={"resources": _to_taggable(resources)})

    def fetch_all_droplets(self):
        r"""
        Returns a generator that yields all of the droplets to which the tag is
        currently applied

        :rtype: generator of `Droplet`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return map(api._droplet, api.paginate('/v2/droplets', 'droplets',
                                              params={"tag_name": self.name}))

    def delete_all_droplets(self):
        """
        Delete all of the droplets to which the tag is applied

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request('/v2/droplets', method='DELETE',
                                   params={"tag_name": self.name})

    def act_on_droplets(self, **data):
        r"""
        Perform an arbitrary action on all of the droplets to which the tag is
        applied.  ``data`` will be serialized as JSON and POSTed to the proper
        API endpoint.  All currently-documented actions require the POST body
        to be a JSON object containing, at a minimum, a ``"type"`` field.

        :return: a generator of `Action`\ s representing the in-progress
            operations on the droplets
        :rtype: generator of `Action`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return map(api._action, api.request('/v2/droplets/actions', method='POST', params={"tag_name": self.name}, data=data)["actions"])

    def power_cycle(self):
        """ TODO """
        return self.act_on_droplets(type='power_cycle')

    def power_on(self):
        """ TODO """
        return self.act_on_droplets(type='power_on')

    def power_off(self):
        """ TODO """
        return self.act_on_droplets(type='power_off')

    def shutdown(self):
        """ TODO """
        return self.act_on_droplets(type='shutdown')

    def enable_private_networking(self):
        """ TODO """
        return self.act_on_droplets(type='enable_private_networking')

    def enable_ipv6(self):
        """ TODO """
        return self.act_on_droplets(type='enable_ipv6')

    def enable_backups(self):
        """ TODO """
        return self.act_on_droplets(type='enable_backups')

    def disable_backups(self):
        """ TODO """
        return self.act_on_droplets(type='disable_backups')

    def snapshot(self, name):
        """ TODO """
        return self.act_on_droplets(type='snapshot', name=name)


def _to_taggable(resources):
    res = []
    for r in resources:
        try:
            res.append(r._taggable())
        except (AttributeError, TypeError):
            if isinstance(r, Resource):
                raise TypeError('Tagging {0!r} objects is not supported'
                                .format(r._class()))
            else:
                # Assume `r` is a "primitive" type
                res.append(r)
    return res
