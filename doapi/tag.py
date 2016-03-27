from six          import iteritems, string_types
from six.moves    import map
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
        res = [r if isinstance(r, dict) else r._taggable() for r in resources]
        self.doapi_manager.request(self.url + '/resources', method='POST',
                                   data={"resources": res})

    def remove(self, *resources):
        res = [r if isinstance(r, dict) else r._taggable() for r in resources]
        self.doapi_manager.request(self.url + '/resources', method='DELETE',
                                   data={"resources": res})

    def fetch_all_droplets(self):
        api = self.doapi_manager
        return map(api._droplet, api.paginate('/v2/droplets', 'droplets',
                                              params={"tag_name": self.name}))

    def delete_all_droplets(self):
        self.doapi_manager.request('/v2/droplets', method='DELETE',
                                   params={"tag_name": self.name})

    def act_on_droplets(self, **data):
        api = self.doapi_manager
        return map(api._action, api.request('/v2/droplets/actions', method='POST', params={"tag_name": self.name}, data=data)["actions"])

    def power_cycle(self):
        return self.act_on_droplets(type='power_cycle')

    def power_on(self):
        return self.act_on_droplets(type='power_on')

    def power_off(self):
        return self.act_on_droplets(type='power_off')

    def shutdown(self):
        return self.act_on_droplets(type='shutdown')

    def enable_private_networking(self):
        return self.act_on_droplets(type='enable_private_networking')

    def enable_ipv6(self):
        return self.act_on_droplets(type='enable_ipv6')

    def enable_backups(self):
        return self.act_on_droplets(type='enable_backups')

    def disable_backups(self):
        return self.act_on_droplets(type='disable_backups')

    def snapshot(self, name):
        return self.act_on_droplets(type='snapshot', name=name)
