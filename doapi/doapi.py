import json
from   time         import sleep, time
import requests
from   six          import iteritems, string_types
from   six.moves    import map  # pylint: disable=redefined-builtin
from   .base        import Region, Size, Account, DropletUpgrade, DOAPIError
from   .action      import Action
from   .domain      import Domain
from   .droplet     import Droplet
from   .floating_ip import FloatingIP
from   .image       import Image
from   .ssh_key     import SSHKey

class doapi(object):
    """
    The primary class for interacting with the DigitalOcean API, used for
    creating and fetching resources.  The resource objects returned by these
    methods have methods of their own for manipulating them individually.

    :param str api_token: the API token to use for authentication
    :param string endpoint: the URL relative to which requests will be made
    :param number timeout: the ``timeout`` value to use when making requests
    :type timeout: float, tuple, or `None`
    :param number wait_interval: the default number of seconds that "wait"
        operations will sleep for between requests
    :param wait_time: the default number of seconds after which "wait"
        operations will return, or `None` or a negative number to wait
        indefinitely
    :type wait_type: number or `None`
    :param per_page: the default number of objects that :meth:`paginate` will
        fetch on each request, or `None` to leave unspecified
    :type per_page: integer or `None`
    """

    #: The official DigitalOcean API endpoint
    DEFAULT_ENDPOINT = 'https://api.digitalocean.com'

    def __init__(self, api_token, endpoint=DEFAULT_ENDPOINT, timeout=None,
                 wait_interval=5, wait_time=None, per_page=None):
        #: The API token used for authentication
        self.api_token = api_token
        #: The API endpoint URL relative to which requests will be made
        self.endpoint = endpoint
        #: The ``timeout`` value to use when making requests; see
        #: `the requests documentation
        #: <http://www.python-requests.org/en/latest/user/advanced/#timeouts>`_
        #: for more information
        self.timeout = timeout
        #: The default number of seconds that :meth:`wait_droplets`,
        #: :meth:`wait_actions`, and the ``wait`` methods of `Action`,
        #: `Droplet`, `FloatingIP`, and `Image` will sleep for between requests
        self.wait_interval = wait_interval
        #: The default number of seconds after which "wait" operations will
        #: return, or `None` or a negative number to wait indefinitely
        self.wait_time = wait_time
        #: The default number of objects that :meth:`paginate` will fetch on
        #: each request, or `None` to leave unspecified
        self.per_page = per_page
        #: The :class:`requests.Response` object returned for the most recent
        #: request, or `None` if no requests have been made yet
        self.last_response = None
        #: The ``meta`` field in the body of the most recent response, or
        #: `None` if there was no such field, no requests have been made yet,
        #: or the last response was an error
        self.last_meta = None
        #: The :class:`requests.Session` object through which all requests are
        #: performed
        self.session = requests.Session()

    def close(self):
        """
        Close the session.  All API methods will be unusable after calling this
        method.

        :return: `None`
        """
        self.session.close()

    def request(self, url, params=None, data=None, method='GET'):
        """
        Perform an HTTP request and return the response body as a decoded JSON
        value

        :param str url: the URL to make the request of.  If ``url`` begins with
            a forward slash, :attr:`endpoint` is prepended to it; otherwise,
            ``url`` is treated as an absolute URL.
        :param dict params: parameters to add to the URL's query string
        :param data: a value to send in the body of the request.  If ``data``
            is not a string, it will be serialized as JSON before sending;
            either way, the :mailheader:`Content-Type` header of the request
            will be set to :mimetype:`application/json`.  Note that a ``data``
            value of `None` means "Don't send any data"; to send an actual
            `None` value, convert it to JSON (i.e., the string ``"null"``)
            first.
        :param str method: the HTTP method to use: ``"GET"``, ``"POST"``,
            ``"PUT"``, or ``"DELETE"`` (case-insensitive); default: ``"GET"``
        :return: a decoded JSON value, or `None` if no data was returned
        :rtype: `list` or `dict` (depending on the request) or `None`
        :raises ValueError: if ``method`` is an invalid value
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if url.startswith('/'):
            url = self.endpoint + url
        attrs = {
            "headers": {"Authorization": "Bearer " + self.api_token},
            "params": params if params is not None else {},
            "timeout": self.timeout,
        }
        method = method.upper()
        if data is not None:
            if not isinstance(data, string_types):
                data = json.dumps(data)
            attrs["data"] = data
            attrs["headers"]["Content-Type"] = "application/json"
        if method == 'GET':
            r = self.session.get(url, **attrs)
        elif method == 'POST':
            r = self.session.post(url, **attrs)
        elif method == 'PUT':
            r = self.session.put(url, **attrs)
        elif method == 'DELETE':
            r = self.session.delete(url, **attrs)
        else:
            raise ValueError('Unrecognized HTTP method: ' + repr(method))
        self.last_response = r
        self.last_meta = None
        if not r.ok:
            raise DOAPIError(r)
        if r.text.strip():
            # Even when returning "no content", the API can still return
            # whitespace.
            response = r.json()
            try:
                self.last_meta = response["meta"]
            except (KeyError, TypeError):
                pass
            return response

    @property
    def last_rate_limit(self):
        """
        A `dict` of the rate limit information returned in the most recent
        response, or `None` if no requests have been made yet.  The `dict`
        consists of all headers whose names begin with ``"RateLimit"`` (case
        insensitive).

        The DigitalOcean API specifies the following rate limit headers:

        :var string RateLimit-Limit: the number of requests that can be made
            per hour
        :var string RateLimit-Remaining: the number of requests remaining until
            the limit is reached
        :var string RateLimit-Reset: the Unix timestamp for the time when the
            oldest request will expire from rate limit consideration
        """
        if self.last_response is None:
            return None
        else:
            return {k:v for k,v in iteritems(self.last_response.headers)
                        if k.lower().startswith('ratelimit')}

    def paginate(self, url, key, params=None):
        """
        Fetch a sequence of paginated resources from the API endpoint.  The
        initial request to ``url`` and all subsequent requests must respond
        with a JSON object; the field specified by ``key`` must be a list,
        whose elements will be yielded, and the next request will be made to
        the URL in the ``.links.pages.next`` field until the responses no
        longer contain that field.

        :param str url: the URL to make the initial request of.  If ``url``
            begins with a forward slash, :attr:`endpoint` is prepended to it;
            otherwise, ``url`` is treated as an absolute URL.
        :param str key: the field on each page containing a list of values to
            yield
        :param dict params: parameters to add to the initial URL's query
            string.  A ``"per_page"`` parameter may be included to override
            the default :attr:`per_page` setting.
        :rtype: generator of decoded JSON values
        :raises ValueError: if a response body is not an object or ``key`` is
            not one of its keys
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if params is None:
            params = {}
        if self.per_page is not None and "per_page" not in params:
            params["per_page"] = self.per_page
        page = self.request(url, params=params)
        while True:
            try:
                objects = page[key]
            except (KeyError, TypeError):
                raise ValueError('{0!r}: not a key of the response body'\
                                 .format(key))
            for obj in objects:
                yield obj
            try:
                url = page["links"]["pages"]["next"]
            except KeyError:
                break
            page = self.request(url)

    def _droplet(self, obj):
        """
        Construct a `Droplet` object belonging to the `doapi` object.  ``obj``
        may be a droplet ID, a dictionary of droplet fields, or another
        `Droplet` object (which will be shallow-copied).  The resulting
        `Droplet` will only contain the information in ``obj``; no data will be
        sent to or from the API endpoint.

        :type obj: integer, `dict`, or `Droplet`
        :rtype: Droplet
        """
        return Droplet(obj, doapi_manager=self)

    def fetch_droplet(self, obj):
        """
        Fetch a droplet by ID number

        :param obj: the ID of the droplet, a `dict` with an ``"id"`` field,
            or a `Droplet` object (to re-fetch the same droplet)
        :type obj: integer, `dict`, or `Droplet`
        :rtype: Droplet
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._droplet(obj).fetch()

    def fetch_all_droplets(self):
        r"""
        Returns a generator that yields all of the droplets belonging to the
        account

        :rtype: generator of `Droplet`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return map(self._droplet, self.paginate('/v2/droplets', 'droplets'))

    def fetch_all_droplet_upgrades(self):
        r"""
        Returns a generator that yields `DropletUpgrade` objects describing
        droplets that are scheduled to be upgraded

        :rtype: generator of `DropletUpgrade`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        for obj in self.request('/v2/droplet_upgrades'):
            yield DropletUpgrade(obj, doapi_manager=self)

    def create_droplet(self, name, image, size, region, ssh_keys=None,
                       backups=None, ipv6=None, private_networking=None,
                       user_data=None, **kwargs):
        """
        Create a new droplet.  All fields other than ``name``, ``image``,
        ``size``, and ``region`` are optional and will be omitted from the API
        request if not specified.

        The returned `Droplet` object will represent the droplet at the moment
        of creation; the actual droplet may not be active yet and may not have
        even been assigned an IP address.  To wait for the droplet to activate,
        use the `Droplet`'s :meth:`~Droplet.wait` method.

        :param str name: a name for the droplet
        :param image: the image ID, slug, or `Image` object representing the
            base image to use for the droplet
        :type image: integer, string, or `Image`
        :param size: the slug or `Size` object representing the size of the new
            droplet
        :type size: string or `Size`
        :param region: the slug or `Region` object representing the region in
            which to create the droplet
        :type region: string or `Region`
        :param iterable ssh_keys: an iterable of SSH key resource IDs, SSH key
            fingerprints, and/or `SSHKey` objects specifying the public keys to
            add to the new droplet's :file:`/root/.ssh/authorized_keys` file
        :param bool backups: whether to enable automatic backups on the new
            droplet
        :param bool ipv6: whether to enable IPv6 on the new droplet
        :param bool private_networking: whether to enable private networking
            for the new droplet
        :param str user_data: a string of user data/metadata for the droplet
        :param kwargs: additional fields to include in the API request
        :return: the new droplet resource
        :rtype: Droplet
        :raises DOAPIError: if the API endpoint replies with an error
        """
        data = {
            "name": name,
            "image": image.id if isinstance(image, Image) else image,
            "size": str(size),
            "region": str(region),
        }
        if ssh_keys is not None:
            data["ssh_keys"] = [k._id if isinstance(k, SSHKey) else k
                                      for k in ssh_keys]
        if backups is not None:
            data["backups"] = backups
        if ipv6 is not None:
            data["ipv6"] = ipv6
        if private_networking is not None:
            data["private_networking"] = private_networking
        if user_data is not None:
            data["user_data"] = user_data
        data.update(kwargs)
        return self._droplet(self.request('/v2/droplets', method='POST',
                                          data=data)["droplet"])

    def create_multiple_droplets(self, names, image, size, region,
                                 ssh_keys=None, backups=None, ipv6=None,
                                 private_networking=None, user_data=None,
                                 **kwargs):
        r"""
        Create multiple new droplets at once with the same image, size, etc.,
        differing only in name.  All fields other than ``names``, ``image``,
        ``size``, and ``region`` are optional and will be omitted from the API
        request if not specified.

        The returned `Droplet` objects will represent the droplets at the
        moment of creation; the actual droplets may not be active yet and may
        not have even been assigned IP addresses.  To wait for the droplets to
        activate, use their :meth:`~Droplet.wait` method or `wait_droplets`.

        :param names: the names for the new droplets
        :type names: list of strings
        :param image: the image ID, slug, or `Image` object representing the
            base image to use for the droplets
        :type image: integer, string, or `Image`
        :param size: the slug or `Size` object representing the size of the new
            droplets
        :type size: string or `Size`
        :param region: the slug or `Region` object representing the region in
            which to create the droplets
        :type region: string or `Region`
        :param iterable ssh_keys: an iterable of SSH key resource IDs, SSH key
            fingerprints, and/or `SSHKey` objects specifying the public keys to
            add to the new droplets' :file:`/root/.ssh/authorized_keys` files
        :param bool backups: whether to enable automatic backups on the new
            droplets
        :param bool ipv6: whether to enable IPv6 on the new droplets
        :param bool private_networking: whether to enable private networking
            for the new droplets
        :param str user_data: a string of user data/metadata for the droplets
        :param kwargs: additional fields to include in the API request
        :return: the new droplet resources
        :rtype: list of `Droplet`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        data = {
            "names": names,
            "image": image.id if isinstance(image, Image) else image,
            "size": str(size),
            "region": str(region),
        }
        if ssh_keys is not None:
            data["ssh_keys"] = [k._id if isinstance(k, SSHKey) else k
                                      for k in ssh_keys]
        if backups is not None:
            data["backups"] = backups
        if ipv6 is not None:
            data["ipv6"] = ipv6
        if private_networking is not None:
            data["private_networking"] = private_networking
        if user_data is not None:
            data["user_data"] = user_data
        data.update(kwargs)
        return list(map(self._droplet, self.request('/v2/droplets',
                                                    method='POST',
                                                    data=data)["droplets"]))

    def fetch_all_droplet_neighbors(self):
        r"""
        Returns a generator of all sets of multiple droplets that are running
        on the same physical hardware

        :rtype: generator of lists of `Droplet`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        for hood in self.paginate('/v2/reports/droplet_neighbors', 'neighbors'):
            yield list(map(self._droplet, hood))

    def wait_droplets(self, droplets, status=None, wait_interval=None,
                                                   wait_time=None):
        r"""
        Poll the server periodically until all droplets in ``droplets`` have
        reached some final state, yielding each `Droplet`'s final value when
        it's done.  If ``status`` is non-`None`, ``wait_droplets`` will wait
        for each droplet's ``status`` field to equal the given value;
        otherwise, it will wait for the most recent action on each droplet to
        finish.

        If ``wait_time`` is exceeded or a `KeyboardInterrupt` is caught, any
        remaining droplets are returned immediately without waiting for
        completion.

        :param iterable droplets: an iterable of `Droplet`\ s and/or other
            values that are acceptable arguments to :meth:`fetch_droplet`
        :param status: When non-`None`, the desired value for the ``status``
            field of each `Droplet`, which should be one of
            `Droplet.STATUS_ACTIVE`, `Droplet.STATUS_ARCHIVE`,
            `Droplet.STATUS_NEW`, and `Droplet.STATUS_OFF`.  (For the sake of
            forwards-compatibility, any other value is accepted as well.)
        :type status: string or `None`
        :param number wait_interval: how many seconds to sleep between
            requests; defaults to :attr:`wait_interval` if not specified or
            `None`
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to :attr:`wait_time` if not specified or `None`
        :rtype: generator of `Droplet`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        droplets = map(self._droplet, droplets)
        if status is None:
            return map(Action.fetch_resource,
                       self.wait_actions(map(Droplet.fetch_last_action,
                                             droplets),
                                         wait_interval, wait_time))
        else:
            return self._wait(droplets, lambda d: d.status == status,
                              wait_interval, wait_time)

    def _action(self, obj):
        """
        Construct an `Action` object belonging to the `doapi` object.  ``obj``
        may be an action ID, a dictionary of action fields, or another `Action`
        object (which will be shallow-copied).  The resulting `Action` will
        only contain the information in ``obj``; no data will be sent to or
        from the API endpoint.

        :type obj: integer, `dict`, or `Action`
        :rtype: Action
        """
        return Action(obj, doapi_manager=self)

    def fetch_action(self, obj):
        """
        Fetch an action by ID number

        :param obj: the ID of the action, a `dict` with an ``"id"`` field,
            or an `Action` object (to re-fetch the same action)
        :type obj: integer, `dict`, or `Action`
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._action(obj).fetch()

    def fetch_last_action(self):
        """
        Fetch the most recent action performed on the account, or `None` if
        no actions have been performed yet.  If multiple actions were triggered
        simultaneously, the choice of which to return is undefined.

        :rtype: `Action` or `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        # Naive implementation:
        acts = self.request('/v2/actions')["actions"]
        return self._action(acts[0]) if acts else None
        # Slow yet guaranteed-correct implementation:
        #return max(self.fetch_all_actions(), key=lambda a: a.started_at)

    def fetch_all_actions(self):
        r"""
        Returns a generator that yields all of the actions associated with the
        account

        :rtype: generator of `Action`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return map(self._action, self.paginate('/v2/actions', 'actions'))

    def wait_actions(self, actions, wait_interval=None, wait_time=None):
        r"""
        Poll the server periodically until all actions in ``actions`` have
        either completed or errored out, yielding each `Action`'s final value
        as it ends.  If ``wait_time`` is exceeded or a `KeyboardInterrupt` is
        caught, any remaining actions are returned immediately without waiting
        for completion.

        :param iterable actions: an iterable of `Action`\ s and/or other values
            that are acceptable arguments to :meth:`fetch_action`
        :param number wait_interval: how many seconds to sleep between
            requests; defaults to :attr:`wait_interval` if not specified or
            `None`
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to :attr:`wait_time` if not specified or `None`
        :rtype: generator of `Action`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._wait(map(self._action, actions), lambda a: a.done,
                          wait_interval, wait_time)

    def _ssh_key(self, obj):
        """
        Construct an `SSHKey` object belonging to the `doapi` object.  ``obj``
        may be an SSH key ID number, an SSH key fingerprint, a dictionary of
        SSH key fields, or another `SSHKey` object (which will be
        shallow-copied).  The resulting `SSHKey` will only contain the
        information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: integer, string, `dict`, or `SSHKey`
        :rtype: SSHKey
        """
        return SSHKey(obj, doapi_manager=self)

    def fetch_ssh_key(self, obj):
        """
        Fetch an SSH public key by ID number or fingerprint

        :param obj: the ID or fingerprint of the SSH key, a `dict` with an
            ``"id"`` or ``"fingerprint"`` field, or an `SSHKey` object (to
            re-fetch the same SSH key)
        :type obj: integer, string, `dict`, or `SSHKey`
        :rtype: SSHKey
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._ssh_key(obj).fetch()

    def fetch_all_ssh_keys(self):
        r"""
        Returns a generator that yields all of the SSH public keys belonging to
        the account

        :rtype: generator of `SSHKey`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return map(self._ssh_key, self.paginate('/v2/account/keys', 'ssh_keys'))

    def create_ssh_key(self, name, public_key, **kwargs):
        """
        Add a new SSH public key resource to the account

        :param str name: the name to give the new SSH key resource
        :param str public_key: the text of the public key to register, in the
            form used by :file:`authorized_keys` files
        :param kwargs: additional fields to include in the API request
        :return: the new SSH key resource
        :rtype: SSHKey
        :raises DOAPIError: if the API endpoint replies with an error
        """
        data = {"name": name, "public_key": public_key}
        data.update(kwargs)
        return self._ssh_key(self.request('/v2/account/keys', method='POST',
                                          data=data)["ssh_key"])

    def _image(self, obj):
        """
        Construct an `Image` object belonging to the `doapi` object.  ``obj``
        may be an image ID, a dictionary of image fields, or another `Image`
        object (which will be shallow-copied).  The resulting `Image` will only
        contain the information in ``obj``; no data will be sent to or from the
        API endpoint.

        :type obj: integer, `dict`, or `Image`
        :rtype: Image
        """
        return Image(obj, doapi_manager=self)

    def fetch_image(self, obj):
        """
        Fetch an image by ID number

        :param obj: the ID of the image, a `dict` with an ``"id"`` field, or
            an `Image` object (to re-fetch the same image)
        :type obj: integer, `dict`, or `Image`
        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._image(obj).fetch()

    def fetch_image_by_slug(self, slug):
        """
        Fetch an image by its slug

        :param str slug: the slug of the image to fetch
        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._image(self.request('/v2/images/' + slug)["image"])

    def fetch_all_images(self, type=None, private=False):
        r"""
        Returns a generator that yields all of the images available to the
        account

        :param type: the type of images to fetch: ``"distribution"``,
            ``"application"``, or all (`None`); default: `None`
        :type type: string or None
        :param bool private: whether to only return the user's private images;
            default: `False` (i.e., return all images)
        :rtype: generator of `Image`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        params = {}
        if type is not None:
            params["type"] = type
        if private:
            params["private"] = 'true'
        return map(self._image, self.paginate('/v2/images', 'images',
                                              params=params))

    def fetch_all_distribution_images(self):
        r"""
        Returns a generator that yields all of the distribution images
        available to the account

        :rtype: generator of `Image`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.fetch_all_images(type='distribution')

    def fetch_all_application_images(self):
        r"""
        Returns a generator that yields all of the application images available
        to the account

        :rtype: generator of `Image`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.fetch_all_images(type='application')

    def fetch_all_private_images(self):
        r"""
        Returns a generator that yields all of the user's private images

        :rtype: generator of `Image`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.fetch_all_images(private=True)

    def _region(self, obj):
        """
        Construct a `Region` object belonging to the `doapi` object.  ``obj``
        may be a dictionary of region fields or another `Region` object (which
        will be shallow-copied).  The resulting `Region` will only contain the
        information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: `dict` or `Region`
        :rtype: Region
        """
        return Region(obj, doapi_manager=self)

    def fetch_all_regions(self):
        r"""
        Returns a generator that yields all of the regions available to the
        account

        :rtype: generator of `Region`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return map(self._region, self.paginate('/v2/regions', 'regions'))

    def _size(self, obj):
        """
        Construct a `Size` object belonging to the `doapi` object.  ``obj`` may
        be a dictionary of size fields or another `Size` object (which will be
        shallow-copied).  The resulting `Size` will only contain the
        information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: `dict` or `Size`
        :rtype: Size
        """
        return Size(obj, doapi_manager=self)

    def fetch_all_sizes(self):
        r"""
        Returns a generator that yields all of the sizes available to the
        account

        :rtype: generator of `Size`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return map(self._size, self.paginate('/v2/sizes', 'sizes'))

    def fetch_account(self):
        """
        Returns an `Account` object representing the user's account

        :rtype: Account
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return Account(self.request('/v2/account')["account"],
                       doapi_manager=self)

    def _domain(self, obj):
        """
        Construct a `Domain` object belonging to the `doapi` object.  ``obj``
        may be a domain name, a dictionary of domain fields, or another
        `Domain` object (which will be shallow-copied).  The resulting `Domain`
        will only contain the information in ``obj``; no data will be sent to
        or from the API endpoint.

        :type obj: string, `dict`, or `Domain`
        :rtype: Domain
        """
        return Domain(obj, doapi_manager=self)

    def fetch_domain(self, obj):
        """
        Fetch a domain by FQDN

        :param obj: the domain name, a `dict` with a ``"name"`` field, or a
            `Domain` object (to re-fetch the same domain)
        :type obj: string, `dict`, or `Domain`
        :rtype: Domain
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._domain(obj).fetch()

    def fetch_all_domains(self):
        r"""
        Returns a generator that yields all of the domains belonging to the
        account

        :rtype: generator of `Domain`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return map(self._domain, self.paginate('/v2/domains', 'domains'))

    def create_domain(self, name, ip_address, **kwargs):
        """
        Add a new domain name resource to the account.

        Note that this method does not actually register a new domain name; it
        merely configures DigitalOcean's nameservers to provide DNS resolution
        for the domain.  See `How To Set Up a Host Name with DigitalOcean
        <https://www.digitalocean.com/community/tutorials/how-to-set-up-a-host-name-with-digitalocean>`_
        for more information.

        :param str name: the domain name to add
        :param ip_address: the IP address to which the domain should point
        :type ip_address: string or `FloatingIP`
        :param kwargs: additional fields to include in the API request
        :return: the new domain resource
        :rtype: Domain
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if isinstance(ip_address, FloatingIP):
            ip_address = ip_address.ip
        data = {"name": name, "ip_address": ip_address}
        data.update(kwargs)
        return self._domain(self.request('/v2/domains', method='POST',
                                                        data=data)["domain"])

    def _floating_ip(self, obj):
        """
        Construct a `FloatingIP` object belonging to the `doapi` object.
        ``obj`` may be an IP address (as a string or 32-bit integer), a
        dictionary of floating IP fields, or another `FloatingIP` object (which
        will be shallow-copied).  The resulting `FloatingIP` will only contain
        the information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: string, integer, `dict`, or `FloatingIP`
        :rtype: FloatingIP
        """
        return FloatingIP(obj, doapi_manager=self)

    def fetch_floating_ip(self, obj):
        """
        Fetch a floating IP

        :param obj: an IP address (as a string or 32-bit integer), a `dict`
            with an ``"ip"`` field, or a `FloatingIP` object (to re-fetch the
            same floating IP)
        :type obj: string, integer, `dict`, or `FloatingIP`
        :rtype: FloatingIP
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._floating_ip(obj).fetch()

    def fetch_all_floating_ips(self):
        r"""
        Returns a generator that yields all of the floating IPs belonging to
        the account

        :rtype: generator of `FloatingIP`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return map(self._floating_ip, self.paginate('/v2/floating_ips',
                                                    'floating_ips'))

    def create_floating_ip(self, droplet_id=None, region=None, **kwargs):
        """
        Create a new floating IP assigned to a droplet or reserved to a region.
        Either ``droplet_id`` or ``region`` must be specified, but not both.

        The returned `FloatingIP` object will represent the IP at the moment of
        creation; if the IP address is supposed to be assigned to a droplet,
        the assignment may not have been completed at the time the object is
        returned.  To wait for the assignment to complete, use the
        `FloatingIP`'s :meth:`~FloatingIP.wait` method.

        :param droplet_id: the droplet to assign the floating IP to as either
            an ID or a `Droplet` object
        :type droplet_id: integer or `Droplet`
        :param region: the region to reserve the floating IP to as either a
            slug or a `Region` object
        :type region: string or `Region`
        :param kwargs: additional fields to include in the API request
        :return: the new floating IP
        :rtype: FloatingIP
        :raises TypeError: if both ``droplet_id`` & ``region`` or neither of
            them are defined
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if (droplet_id is None) == (region is None):
            ### TODO: Is TypeError the right type of error?
            raise TypeError('Exactly one of "droplet_id" and "region" must be'
                            ' specified')
        if droplet_id is not None:
            if isinstance(droplet_id, Droplet):
                droplet_id = droplet_id.id
            data = {"droplet_id": droplet_id}
        else:
            if isinstance(region, Region):
                region = region.slug
            data = {"region": region}
        data.update(kwargs)
        return self._floating_ip(self.request('/v2/floating_ips', method='POST',
                                              data=data)["floating_ip"])

    def __eq__(self, other):
        return type(self) is type(other) and vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def _wait(self, objects, isdone, wait_interval=None, wait_time=None):
        r"""
        Calls the ``fetch`` method of each object in ``objects`` periodically
        until ``isdone`` returns true on each one, yielding the final value of
        each object as soon as it succeeds.  If ``wait_time`` is exceeded or a
        `KeyboardInterrupt` is caught, any remaining objects are returned
        immediately without waiting for completion.

        :param iterable objects: an iterable of objects with ``fetch`` methods
            (presumably `Resource`\ s)
        :param number wait_interval: how many seconds to sleep between
            requests; defaults to :attr:`wait_interval` if not specified or
            `None`
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to :attr:`wait_time` if not specified or `None`
        :rtype: generator
        :raises DOAPIError: if the API endpoint replies with an error
        """
        objects = list(objects)
        if not objects:
            return
        if wait_interval is None:
            wait_interval = self.wait_interval
        if wait_time < 0:
            end_time = None
        else:
            if wait_time is None:
                wait_time = self.wait_time
            if wait_time is None or wait_time < 0:
                end_time = None
            else:
                end_time = time() + wait_time
        while end_time is None or time() < end_time:
            loop_start = time()
            next_objs = []
            for o in objects:
                obj = o.fetch()
                if isdone(obj):
                    yield obj
                else:
                    next_objs.append(obj)
            objects = next_objs
            if not objects:
                break
            loop_end = time()
            time_left = wait_interval - (loop_end - loop_start)
            if end_time is not None:
                time_left = min(time_left, end_time - loop_end)
            if time_left > 0:
                try:
                    sleep(time_left)
                except KeyboardInterrupt:
                    break
        for o in objects:
            yield o
