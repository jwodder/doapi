from .base import ResourceWithID, Region, DOAPIError

class Action(ResourceWithID):
    """
    An action resource, representing a change made to another resource.

    Actions are created in response to almost all mutating requests on
    droplets, images, and floating IPs, and they can be retrieved with the
    :meth:`doapi.fetch_action`, :meth:`doapi.fetch_last_action`,
    :meth:`doapi.fetch_all_actions` methods as well as the
    ``fetch_all_actions``, ``fetch_last_action``, and ``fetch_current_action``
    methods of `Droplet`, `Image`, and `FloatingIP`.

    The DigitalOcean API specifies the following fields for action objects:

    :var id: a unique identifier for the action
    :vartype id: int

    :var status: the current status of the action: ``"in-progress"``,
        ``"completed"``, or ``"errored"``
    :vartype status: string

    :var type: the type of action performed
    :vartype type: string

    :var started_at: date & time of the action's initiation as an ISO 8601
        timestamp
    :vartype started_at: string

    :var completed_at: date & time of the action's completion as an ISO 8601
        timestamp
    :vartype completed_at: string

    :var resource_id: the unique ID of the resource that the action operated
        on.  If the resource was a droplet or image, this will be its ``id``
        field.  If the resource was a floating IP, this will be the IP address
        as a 32-bit integer.
    :vartype resource_id: int

    :var resource_type: the type of resource that the action operated on:
        ``"droplet"``, ``"image"``, or ``"floating_ip"``
    :vartype resource_type: string

    :var region: the region in which the action occurred
    :vartype region: `Region`

    :var region_slug: the unique slug identifier for the region in which the
        action occurred
    :vartype region_slug: string

    Under normal/non-pathological circumstances, none of these methods should
    ever raise a `DOAPIError`.
    """

    def __init__(self, state=None, **extra):
        """ TODO """
        super(Action, self).__init__(state, **extra)
        if self.get('region') is not None and \
                not isinstance(self.region, Region):
            self.region = Region(self.region, doapi_manager=self.doapi_manager)

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
        return self._url('/v2/actions/' + str(self.id))

    def fetch(self):
        """
        Fetch & return a new `Action` object representing the action's current
        state

        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return api._action(api.request(self.url)["action"])

    def fetch_resource(self):
        """
        Fetch & return the resource that the action operated on, or ``None`` if
        the resource no longer exists (specifically, if the API returns a 404)

        :rtype: `Droplet`, `Image`, `FloatingIP`, or ``None``
        :raises ValueError: if the action has an unknown ``resource_type``
            (This indicates a deficiency in the library; please report it!)
        :raises DOAPIError: if the API endpoint replies with a non-404 error
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
