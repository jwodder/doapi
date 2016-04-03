import collections
from   datetime  import datetime
import json
import numbers
import pyrfc3339
from   six       import iteritems
from   six.moves import map  # pylint: disable=redefined-builtin

class Resource(collections.MutableMapping):
    _meta_attrs = ('fields', 'doapi_manager')

    def __init__(self, state=None, **extra):
        # Note that meta attributes in `state` are not recognized as such, but
        # they are in `extra`.
        for attr in self._meta_attrs:
            self.__dict__[attr] = None
        self.fields = {}
        if isinstance(state, self.__class__):
            for attr in self._meta_attrs:
                if attr != 'fields':
                    setattr(self, attr, getattr(state, attr))
            state = state.fields
        elif isinstance(state, Resource):
            raise TypeError('{0!r} object passed to {1!r} constructor'\
                            .format(state._class(), self._class()))
        if state is not None:
            self.fields.update(state)
        for k,v in iteritems(extra):
            setattr(self, k, v)

    def __eq__(self, other):
        return type(self) is type(other) and vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        # Meta attributes have to be omitted or else infinite recursion will
        # occur when trying to print a Droplet.
        return '{0}({1})'.format(self._class(),
                                 ', '.join('{0}={1!r}'.format(k,v)
                                           for k,v in iteritems(self)))

    def __getitem__(self, key):
        return self.fields[key]

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __delitem__(self, key):
        del self.fields[key]

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)

    def __getattr__(self, name):
        try:
            return self.fields[name]
        except KeyError:
            raise AttributeError('{0!r} object has no attribute {1!r}'\
                                 .format(self._class(), name))

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            self.fields[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            del self.__dict__[name]
        else:
            del self.fields[name]

    def _url(self, path):
        try:
            endpoint = self.doapi_manager.endpoint
        except (TypeError, AttributeError):
            endpoint = ''
        return endpoint + path

    def _class(self):
        return self.__class__.__name__


class ResourceWithID(Resource):
    """
    A DigitalOcean API object with a unique integral ``id`` field.  Allows
    construction from an integer and implements ``__int__`` for conversion back
    to the integer.
    """

    def __init__(self, state=None, **extra):
        if isinstance(state, numbers.Integral):
            state = {"id": state}
        super(ResourceWithID, self).__init__(state, **extra)

    def __int__(self):
        """ Convert the resource to its unique ID """
        return self.id


class ResourceWithDroplet(Resource):
    """A Resource with a "`droplet`" meta attribute"""

    _meta_attrs = Resource._meta_attrs + ('droplet',)

    def fetch_droplet(self):
        """
        Fetch the droplet to which the resource belongs, or return `None` if
        the resource's ``droplet`` attribute is `None`

        :rtype: `Droplet` or `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if self.droplet is None:
            return None
        if self.doapi_manager is None:
            return self.droplet.fetch()
            # If `self.droplet` is an int, the user gets the AttributeError
            # they deserve.
        else:
            return self.doapi_manager.fetch_droplet(self.droplet)
            # If `self.droplet` is an int, the user doesn't get the
            # AttributeError they don't deserve.


class Actionable(Resource):
    # Required property: url
    # Required method: fetch

    @property
    def action_url(self):
        """ The endpoint for actions on the specific resource """
        return self.url + '/actions'

    def act(self, **data):
        """
        Perform an arbitrary action on the resource.  ``data`` will be
        serialized as JSON and POSTed to the resource's :attr:`action_url`.
        All currently-documented actions require the POST body to be a JSON
        object containing, at a minimum, a ``"type"`` field.

        :return: an `Action` representing the in-progress operation on the
            resource
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return api._action(api.request(self.action_url, method='POST',
                                       data=data)["action"])

    def wait(self, wait_interval=None, wait_time=None):
        """
        Poll the server periodically until the resource's most recent action
        has either completed or errored out, and return the resource's final
        state afterwards.  If ``wait_time`` is exceeded or a
        `KeyboardInterrupt` is caught, the resource's current state is
        returned immediately without waiting for completion.

        :param number wait_interval: how many seconds to sleep between
            requests; defaults to the `doapi` object's
            :attr:`~doapi.wait_interval` if not specified or `None`
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to the `doapi` object's :attr:`~doapi.wait_time` if not
            specified or `None`
        :return: the resource's final state
        :raises DOAPIError: if the API endpoint replies with an error
        """
        list(self.doapi_manager.wait_actions([self.fetch_last_action()],
                                             wait_interval, wait_time))
        return self.fetch()

    def fetch_all_actions(self):
        r"""
        Returns a generator that yields all of the actions associated with the
        resource

        :rtype: generator of `Action`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return map(api._action, api.paginate(self.action_url, 'actions'))

    def fetch_last_action(self):
        """
        Fetch the most recent action performed on the resource.  If multiple
        actions were triggered simultaneously, the choice of which to return is
        undefined.

        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        # Naive implementation:
        api = self.doapi_manager
        return api._action(api.request(self.action_url)["actions"][0])
        # Slow yet guaranteed-correct implementation:
        #return max(self.fetch_all_actions(), key=lambda a: a.started_at)

    def fetch_current_action(self):
        """
        Fetch the action currently in progress on the resource, or `None` if
        there is no such action

        :rtype: `Action` or `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        lasttime = None
        for a in self.fetch_all_actions():
            # Return the first in-progress Action listed that started on (or
            # after???) the first Action listed.  This is to handle creation of
            # floating IPs assigned to a droplet, as that can cause the assign
            # action to be listed after the reserve/create action, even though
            # the assignment finishes later.
            if lasttime is None:
                lasttime = a.started_at
            elif lasttime > a.started_at:
                return None
            if a.in_progress:
                return a
        return None


class DOEncoder(json.JSONEncoder):
    r"""
    A :class:`json.JSONEncoder` subclass that converts resource objects to
    `dict`\ s for JSONification.  It also converts iterators to lists.
    """
    def default(self, obj):
        if isinstance(obj, Resource):
            return obj.fields
        elif isinstance(obj, datetime):
            return toISO8601(obj)
        elif isinstance(obj, collections.Iterator):
            return list(obj)
        else:
            #return json.JSONEncoder.default(self, obj)
            return super(DOEncoder, self).default(obj)


class Region(Resource):
    """
    A region resource, representing a physical datacenter in which droplets can
    be located.

    Available regions can be retreived with the :meth:`doapi.fetch_all_regions`
    method.

    The DigitalOcean API specifies the following fields for region objects:

    :var available: whether new droplets can be created in the region
    :vartype available: bool

    :var features: a list of strings naming the features available in the region
    :vartype features: list of strings

    :var name: a human-readable name for the region
    :vartype name: string

    :var sizes: the slugs of the sizes available in the region
    :vartype sizes: list of strings

    :var slug: the unique slug identifier for the region
    :vartype slug: string
    """

    def __str__(self):
        """ Convert the region to its slug representation """
        return self.slug


class Size(Resource):
    """
    A size resource, representing an option for the amount of RAM, disk space,
    etc. provisioned for a droplet.

    Available sizes can be retreived with the :meth:`doapi.fetch_all_sizes`
    method.

    The DigitalOcean API specifies the following fields for size objects:

    :var available: whether new droplets can be created with this size
    :vartype available: bool

    :var disk: disk size of a droplet of this size in gigabytes
    :vartype disk: number

    :var memory: RAM of a droplet of this size in megabytes
    :vartype memory: number

    :var price_hourly: the hourly cost for a droplet of this size in USD
    :vartype price_hourly: number

    :var price_monthly: the monthly cost for a droplet of this size in USD
    :vartype price_monthly: number

    :var regions: the slugs of the regions in which this size is available
    :vartype regions: list of strings

    :var slug: the unique slug identifier for the size
    :vartype slug: string

    :var transfer: the amount of transfer bandwidth in terabytes available for
        a droplet of this size
    :vartype transfer: number

    :var vcpus: the number of virtual CPUs on a droplet of this size
    :vartype vcpus: int
    """

    def __str__(self):
        """ Convert the size to its slug representation """
        return self.slug


class Account(Resource):
    """
    An account resource describing the user's DigitalOcean account.

    Current details on the user's account can be retrieved with the
    :meth:`doapi.fetch_account` method.

    The DigitalOcean API specifies the following fields for account objects:

    :var droplet_limit: the maximum number of droplets the account may have at
        any one time
    :vartype droplet_limit: int

    :var email: the e-mail address the account used to register for
        DigitalOcean
    :vartype email: string

    :var email_verified: whether the user's account has been verified via
        e-mail
    :vartype email_verified: bool

    :var floating_ip_limit: the maximum number of floating IPs the account may
        have at any one time
    :vartype floating_ip_limit: int

    :var status: the status of the account: ``"active"``, ``"warning"``, or
        ``"locked"``
    :vartype status: string

    :var status_message: a human-readable string describing the status of the
        account
    :vartype status: string

    :var uuid: a UUID for the user
    :vartype uuid: alphanumeric string
    """

    #: The status of an account that is currently active and warning-free
    STATUS_ACTIVE = 'active'

    #: The status of an account that is currently in a "warning" state, e.g.,
    #: from having reached the droplet limit
    STATUS_WARNING = 'warning'

    #: The status of a locked account
    STATUS_LOCKED = 'locked'

    def fetch(self):
        """
        Fetch & return a new `Account` object representing the account's
        current state

        :rtype: Account
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.doapi_manager.fetch_account()

    @property
    def url(self):
        """ The endpoint for operations on the user's account """
        return self._url('/v2/account')


class Kernel(ResourceWithDroplet, ResourceWithID):
    """
    A kernel resource, representing a kernel version that can be installed on a
    given droplet.

    A `Droplet`'s current kernel is stored in its ``kernel`` attribute, and the
    set of kernels available to a given `Droplet` can be retrieved with the
    :meth:`droplet.fetch_all_kernels` method.

    The DigitalOcean API specifies the following fields for kernel objects:

    :var id: a unique identifier for the kernel
    :vartype id: int

    :var name: a human-readable name for the kernel
    :vartype name: string

    :var version: the version string for the kernel
    :vartype version: string

    .. attribute:: droplet

       The `Droplet` associated with the kernel
    """

    pass


class DropletUpgrade(Resource):
    """
    A droplet upgrade resource, representing a scheduled upgrade of a droplet.

    The set of all currently-scheduled upgrades can be retrieved with the
    :meth:`doapi.fetch_all_droplet_upgrades` method.

    The DigitalOcean API specifies the following fields for droplet upgrade
    objects:

    :var date_of_migration: date & time that the droplet will be migrated
    :vartype date_of_migration: datetime.datetime

    :var droplet_id: the ID of the affected droplet
    :vartype droplet_id: int

    :var url: the endpoint for operations on the affected droplet
    :vartype url: string
    """

    def __init__(self, state=None, **extra):
        super(DropletUpgrade, self).__init__(state, **extra)
        if self.get('date_of_migration') is not None and \
                not isinstance(self.date_of_migration, datetime):
            self.date_of_migration = fromISO8601(self.date_of_migration)

    def fetch_droplet(self):
        """
        Fetch the droplet affected by the droplet upgrade

        :rtype: Droplet
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.doapi_manager.fetch_droplet(self.droplet_id)


class Networks(ResourceWithDroplet):
    r"""
    A networks resource, representing a set of network interfaces configured
    for a specific droplet.

    A `Droplet`'s network information is stored in its ``networks`` attribute.

    The DigitalOcean API implicitly specifies the following fields for networks
    objects:

    :var v4: a list of IPv4 interfaces allocated for a droplet
    :vartype v4: list of `NetworkInterface`\ s

    :var v6: a list of IPv6 interfaces allocated for a droplet
    :vartype v6: list of `NetworkInterface`\ s

    .. attribute:: droplet

       The `Droplet` associated with the networks resource
    """
    def __init__(self, state=None, **extra):
        super(Networks, self).__init__(state, **extra)
        meta = {
            "doapi_manager": self.doapi_manager,
            "droplet": self.droplet,
        }
        if self.get("v4"):
            self.v4 = [NetworkInterface(obj, ip_version=4, **meta)
                       for obj in self.v4]
        if self.get("v6"):
            self.v6 = [NetworkInterface(obj, ip_version=6, **meta)
                       for obj in self.v6]


class NetworkInterface(ResourceWithDroplet):
    """
    A network interface resource, representing an IP address allocated to a
    specific droplet.

    A `Droplet`'s network interfaces are listed in its ``networks`` attribute.

    The DigitalOcean API implicitly specifies the following fields for network
    interface objects:

    :var gateway: gateway
    :vartype gateway: string

    :var ip_address: IP address
    :vartype ip_address: string

    :var netmask: netmask
    :vartype ip_address: string

    :var type: ``"public"`` or ``"private"``
    :vartype ip_address: string

    .. attribute:: droplet

       The `Droplet` to which the network interface belongs

    .. attribute:: ip_version

       The IP version used by the interface: ``4`` or ``6``
    """

    _meta_attrs = ResourceWithDroplet._meta_attrs + ('ip_version',)

    def __str__(self):
        """ Show just the IP address of the interface """
        return self.ip_address


class BackupWindow(ResourceWithDroplet):
    """
    A backup window resource, representing an upcoming timeframe in which a
    droplet is scheduled to be backed up.

    A `Droplet`'s next backup window is stored in its ``next_backup_window``
    attribute.

    The DigitalOcean API implicitly specifies the following fields for backup
    window objects:

    :var start: beginning of the window
    :vartype start: datetime.datetime

    :var end: end of the window
    :vartype end: datetime.datetime

    .. attribute:: droplet

       The `Droplet` associated with the backup window
    """

    def __init__(self, state=None, **extra):
        super(BackupWindow, self).__init__(state, **extra)
        if self.get('start') is not None and \
                not isinstance(self.start, datetime):
            self.start = fromISO8601(self.start)
        if self.get('end') is not None and \
                not isinstance(self.end, datetime):
            self.end = fromISO8601(self.end)


class DOAPIError(Exception):
    r"""
    An exception raised in reaction to the API endpoint responding with a 4xx
    or 5xx error.  If the body of the response is a JSON object, its fields
    will be added to the ``DOAPIError``\ 's attributes (except where a
    pre-existing attribute would be overwritten).  DigitalOcean error response
    bodies have been observed to consist of an object with two string fields,
    ``"id"`` and ``"message"``.

    Note that this class is only for representing errors reported by the
    endpoint in response to API requests.  Everything else that can go wrong
    uses the normal Python exceptions.
    """
    def __init__(self, response):
        #: The :class:`requests.Response` object
        self.response = response
        # Taken from requests' raise_for_status:
        #: An error message that should be appropriate for human consumption,
        #: containing the type of HTTP error, the URL that was requested, and
        #: the body of the response.
        self.http_error_msg = ''
        if 400 <= response.status_code < 500:
            self.http_error_msg = '{0.status_code} Client Error: {0.reason}'\
                                  ' for url: {0.url}\n'.format(response)
        elif 500 <= response.status_code < 600:
            self.http_error_msg = '{0.status_code} Server Error: {0.reason}'\
                                  ' for url: {0.url}\n'.format(response)
        self.http_error_msg += response.text
        super(DOAPIError, self).__init__(self.http_error_msg)
        try:
            body = response.json()
        except ValueError:
            pass
        else:
            if isinstance(body, dict):
                for k,v in iteritems(body):
                    if not hasattr(self, k):
                        setattr(self, k, v)

def fromISO8601(stamp):
    return pyrfc3339.parse(stamp)

def toISO8601(dt):
    return pyrfc3339.generate(dt, accept_naive=True)
