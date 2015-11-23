from .base import JSObjectWithID, DOAPIError

class Action(JSObjectWithID):
    """
    TODO

    Under normal/non-pathological circumstances, none of these methods should
    ever raise a `DOAPIError`.
    """

    @property
    def completed(self):
        """ ``True`` iff the action's status is ``"completed"`` """
        return self.status == 'completed'

    @property
    def in_progress(self):
        """ ``True`` iff the action's status is ``"in-progress"`` """
        return self.status == 'in-progress'

    @property
    def done(self):
        """ ``True`` iff the action's status is *not* ``"in-progress"`` """
        return self.status != 'in-progress'

    @property
    def errored(self):
        """ ``True`` iff the action's status is ``"errored"`` """
        return self.status == 'errored'

    @property
    def url(self):
        """ The endpoint for operations on the specific action """
        ### TODO: Look into the conditions under which this has to include the
        ### resource type & ID too
        return self._url('/v2/actions/' + str(self.id))

    def fetch(self):
        """
        Fetch & return a new `Action` object representing the action's current
        state

        :rtype: Action
        """
        api = self.doapi_manager
        return api.action(api.request(self.url)["action"])

    def fetch_resource(self):
        """
        Fetch & return the resource that the action operated on, or ``None`` if
        the resource no longer exists (specifically, if the API returns a 404)

        :rtype: `Droplet`, `Image`, `FloatingIP`, or ``None``
        :raises ValueError: if the action has an unknown ``resource_type``
            (This indicates a deficiency in the library; please report it!)
        """
        try:
            if self.resource_type == "droplet":
                return self.doapi_manager.fetch_droplet(self.resource_id)
            elif self.resource_type == "image":
                return self.doapi_manager.fetch_image(self.resource_id)
            elif self.resource_type == "floating_ip":
                return self.doapi_manager.fetch_floating_ip(self.resource_id)
            else:
                raise ValueError('%r: unknown resource_type'
                                 % (self.resource_type,))
        except DOAPIError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise

    def wait(self, wait_interval=None, wait_time=None):
        """
        Poll the server periodically until the action has either completed or
        errored out and return its final state.  If ``wait_time`` is exceeded
        or a ``KeyboardInterrupt`` is caught, the action's most recently
        fetched state is returned immediately without waiting for completion.

        :param number wait_interval: how many seconds to sleep between
            requests; defaults to the `doapi` object's
            :attr:`~doapi.wait_interval` if not specified or ``None``
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to the `doapi` object's :attr:`~doapi.wait_time` if not
            specified or ``None``
        :return: the action's final state
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return next(self.doapi_manager.wait_actions([self], wait_interval,
                                                            wait_time))
