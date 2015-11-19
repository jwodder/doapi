import json
from   time         import sleep, time
from   urlparse     import urljoin
import requests
from   six          import iteritems
from   six.moves    import map
from   .base        import Region, Size, Account, DropletUpgrade, DOAPIError
from   .action      import Action
from   .domain      import Domain
from   .droplet     import Droplet
from   .floating_ip import FloatingIP
from   .image       import Image
from   .ssh_key     import SSHKey

class doapi(object):
    DEFAULT_ENDPOINT = 'https://api.digitalocean.com'

    def __init__(self, api_token, endpoint=DEFAULT_ENDPOINT, timeout=61,
                 wait_interval=5, wait_time=None, per_page=None):
        """
        Constructs a new `doapi` object

        :param str api_token: the API token to use for authentication
        :param string endpoint: the URL relative to which requests will be made
        :param number timeout: the ``timeout`` value to use when making
            requests
        :type timeout: float, tuple, or ``None``
        :param number wait_interval: the default number of seconds that "wait"
            operations will sleep for between requests
        :param wait_time: the default number of seconds after which "wait"
            operations will return, or ``None`` or a negative number to wait
            indefinitely
        :type wait_type: number or ``None``
        :param per_page: the default number of objects that :meth:`paginate`
            will fetch on each request, or ``None`` to leave unspecified
        :type per_page: integer or ``None``
        """
        #: the API token used for authentication
        self.api_token = api_token
        #: the API endpoint URL relative to which requests will be made
        self.endpoint = endpoint
        #: the ``timeout`` value to use when making requests; see
        #: http://www.python-requests.org/en/latest/user/advanced/#timeouts
        self.timeout = timeout
        #: the default number of seconds that :meth:`wait_droplets`,
        #: :meth:`wait_actions`, and the ``wait`` methods of `Action`,
        #: `Droplet`, `FloatingIP`, and `Image` will sleep for between requests
        self.wait_interval = wait_interval
        #: the default number of seconds after which "wait" operations will
        #: return, or ``None`` or a negative number to wait indefinitely
        self.wait_time = wait_time
        #: the default number of objects that :meth:`paginate` will fetch on
        #: each request, or ``None`` to leave unspecified
        self.per_page = per_page
        #: the `requests.Response
        #: <http://docs.python-requests.org/en/latest/api/#requests.Response>`
        #: object returned for the most recent request, or ``None`` if no
        #: requests have been made yet
        self.last_response = None
        #: the ``meta`` field in the body of the most recent response, or
        #: ``None`` if there was no such field, no requests have been made yet,
        #: or the last response was an error
        self.last_meta = None

    def request(self, url, params={}, data=None, method='GET'):
        """
        Performs an HTTP request and returns the response body as a decoded
        JSON value

        :param str url: the URL to make the request of.  If ``url`` begins with
            a forward slash, :attr:`endpoint` is prepended to it; otherwise,
            ``url`` is treated as an absolute URL.
        :param dict params: parameters to add to the URL's query string
        :param data: a value to serialize as JSON and send in the body of the
            request; only used by the POST and PUT methods
        :param str method: the HTTP method to use: ``"GET"``, ``"POST"``,
            ``"PUT"``, or ``"DELETE"`` (case-insensitive); default: ``"GET"``
        :return: a decoded JSON value, or ``None`` if ``method`` was
            ``"DELETE"``
        :rtype: ``list`` or ``dict`` (depending on the request) or ``None``
        :raises ValueError: if ``method`` is an invalid value
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if url[:1] == "/":
            url = urljoin(self.endpoint, url)
        attrs = {
            "headers": {
                "Authorization": "Bearer " + self.api_token,
                "Content-Type": "application/json"
            },
            "params": params,
            "timeout": self.timeout,
        }
        method = method.upper()
        if method == 'GET':
            r = requests.get(url, **attrs)
        elif method == 'POST':
            r = requests.post(url, data=json.dumps(data), **attrs)
        elif method == 'PUT':
            r = requests.put(url, data=json.dumps(data), **attrs)
        elif method == 'DELETE':
            r = requests.delete(url, **attrs)
        else:
            raise ValueError('Unrecognized HTTP method: ' + repr(method))
        self.last_response = r
        self.last_meta = None
        if 400 <= r.status_code < 600:
            raise DOAPIError(r)
        if method != 'DELETE':
            response = r.json()
            try:
                self.last_meta = response["meta"]
            except (KeyError, TypeError):
                pass
            return response

    @property
    def last_rate_limit(self):
        """
        A ``dict`` of the rate limit information returned in the most recent
        response, or ``None`` if no requests have been made yet.  The ``dict``
        consists of all headers whose names begin with ``"ratelimit"``.
        """
        if self.last_response is None:
            return None
        else:
            return {k:v for k,v in iteritems(self.last_response.headers)
                        if k.startswith('ratelimit')}

    def paginate(self, url, key, params=None):
        """
        Fetches a sequence of paginated resources from the API endpoint.  The
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
        :rtype: a generator of decoded JSON values
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
                raise ValueError('%r: not a key of the response body' % (key,))
            for obj in objects:
                yield obj
            try:
                url = page["links"]["pages"]["next"]
            except KeyError:
                break
            page = self.request(url)

    def droplet(self, obj):
        """
        Constructs a `Droplet` object belonging to the `doapi` object.  ``obj``
        may be a droplet ID, a dictionary of droplet fields, or another
        `Droplet` object (which will be shallow-copied).  The resulting
        `Droplet` will only contain the information in ``obj``; no data will be
        sent to or from the API endpoint.

        :type obj: integer, ``dict``, or `Droplet`
        :rtype: Droplet
        """
        return Droplet(obj, doapi_manager=self)

    def fetch_droplet(self, obj):
        """
        Fetches a droplet by ID number

        :param obj: the ID of the droplet, a ``dict`` with an ``"id"`` field,
            or a `Droplet` object (to re-fetch the same droplet)
        :type obj: integer, ``dict``, or `Droplet`
        :rtype: Droplet
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.droplet(obj).fetch()

    def fetch_all_droplets(self):
        """
        Returns a generator that yields all of the droplets belonging to the
        account in the order that the API endpoint returns them

        :rtype: generator of `Droplet`s
        """
        return map(self.droplet, self.paginate('/v2/droplets', 'droplets'))

    def fetch_all_droplet_upgrades(self):
        """
        Returns a generator that yields `DropletUpgrade` objects describing
        droplets that are scheduled to be upgraded

        :rtype: generator of `DropletUpgrade`s
        """
        for obj in self.request('/v2/droplet_upgrades'):
            yield DropletUpgrade(obj, doapi_manager=self)

    def create_droplet(self, name, image, size, region, ssh_keys=None,
                       backups=None, ipv6=None, private_networking=None,
                       user_data=None):
        """
        Creates a new droplet.  All fields other than ``name``, ``image``,
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
            add to the new droplet's ``/root/.ssh/authorized_keys`` file
        :param bool backups: whether to enable automatic backups on the new
            droplet
        :param bool ipv6: whether to enable IPv6 on the new droplet
        :param bool private_networking: whether to enable private networking
            for the new droplet
        :param str user_data: a string of user data/metadata for the droplet
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
            data["ssh_keys"] = [k.id_or_fingerprint if isinstance(k, SSHKey)
                                                    else k for k in ssh_keys]
        if backups is not None:
            data["backups"] = backups
        if ipv6 is not None:
            data["ipv6"] = ipv6
        if private_networking is not None:
            data["private_networking"] = private_networking
        if user_data is not None:
            data["user_data"] = user_data
        return self.droplet(self.request('/v2/droplets', method='POST',
                                         data=data)["droplet"])

    def fetch_all_droplet_neighbors(self):
        """
        Returns a generator of all sets of multiple droplets that are running
        on the same physical hardware

        :rtype: generator of lists of `Droplet`s
        """
        for hood in self.paginate('/v2/reports/droplet_neighbors', 'neighbors'):
            yield list(map(self.droplet, hood))

    def wait_droplets(self, droplets, status=None, wait_interval=None,
                                                   wait_time=None):
        """
        Polls the server periodically until all droplets in ``droplets`` have
        reached some final state, yielding each `Droplet`'s final value when
        it's done.  If ``status`` is non-``None``, ``wait_droplets`` will wait
        for each droplet's ``status`` field to equal the given value;
        otherwise, it will wait for the most recent action on each droplet to
        finish.

        If ``wait_time`` is exceeded or a ``KeyboardInterrupt`` is caught, any
        remaining droplets are returned immediately without waiting for
        completion.

        :param iterable droplets: an iterable of `Droplet`s and/or other values
            that are acceptable arguments to :meth:`fetch_droplet`
        :param status: When non-``None``, the desired value for the ``status``
            field of each `Droplet`.  ``status`` should be ``"active"``,
            ``"new"``, ``"off"``, or ``"archive"``; no checks of this value are
            performed, so it is possible to inadvertently wait forever for an
            impossible state.
        :type status: string or ``None``
        :param number wait_interval: how many seconds to sleep between
            requests; defaults to :attr:`wait_interval` if not specified or
            ``None``
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to :attr:`wait_time` if not specified or ``None``
        :rtype: generator of `Droplet`s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        droplets = map(self.droplet, droplets)
        if status is None:
            return map(Action.fetch_resource,
                       self.wait_actions(map(Droplet.fetch_last_action,
                                             droplets),
                                         wait_interval, wait_time))
        else:
            return self._wait(droplets, lambda d: d.status == status,
                              wait_interval, wait_time)

    def action(self, obj):
        """
        Constructs an `Action` object belonging to the `doapi` object.  ``obj``
        may be an action ID, a dictionary of action fields, or another `Action`
        object (which will be shallow-copied).  The resulting `Action` will
        only contain the information in ``obj``; no data will be sent to or
        from the API endpoint.

        :type obj: integer, ``dict``, or `Action`
        :rtype: Action
        """
        return Action(obj, doapi_manager=self)

    def fetch_action(self, obj):
        """
        Fetches an action by ID number

        :param obj: the ID of the action, a ``dict`` with an ``"id"`` field,
            or an `Action` object (to re-fetch the same action)
        :type obj: integer, ``dict``, or `Action`
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.action(obj).fetch()

    def fetch_last_action(self):
        """
        Returns the most recent action performed on the account.  If multiple
        actions were triggered simultaneously, the choice of which to return is
        undefined.

        :rtype: Action
        """
        # Naive implementation:
        return self.action(self.request('/v2/actions')["actions"][0])
        # Slow yet guaranteed-correct implementation:
        #return max(self.fetch_all_actions(), key=lambda a: a.started_at)

    def fetch_all_actions(self):
        """
        Returns a generator that yields all of the actions associated with the
        account in the order that the API endpoint returns them

        :rtype: generator of `Action`s
        """
        return map(self.action, self.paginate('/v2/actions', 'actions'))

    def wait_actions(self, actions, wait_interval=None, wait_time=None):
        """
        Polls the server periodically until all actions in ``actions`` have
        either completed or errored out, yielding each `Action`'s final value
        as it ends.  If ``wait_time`` is exceeded or a ``KeyboardInterrupt`` is
        caught, any remaining actions are returned immediately without waiting
        for completion.

        :param iterable actions: an iterable of `Action`s and/or other values
            that are acceptable arguments to :meth:`fetch_action`
        :param number wait_interval: how many seconds to sleep between
            requests; defaults to :attr:`wait_interval` if not specified or
            ``None``
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to :attr:`wait_time` if not specified or ``None``
        :rtype: generator of `Action`s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._wait(map(self.action, actions), lambda a: a.done,
                          wait_interval, wait_time)

    def ssh_key(self, obj):
        """
        Constructs an `SSHKey` object belonging to the `doapi` object.  ``obj``
        may be an SSH key ID number, an SSH key fingerprint, a dictionary of
        SSH key fields, or another `SSHKey` object (which will be
        shallow-copied).  The resulting `SSHKey` will only contain the
        information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: integer, string, ``dict``, or `SSHKey`
        :rtype: SSHKey
        """
        return SSHKey(obj, doapi_manager=self)

    def fetch_ssh_key(self, obj):
        """
        Fetches an SSH public key by ID number or fingerprint

        :param obj: the ID or fingerprint of the SSH key, a ``dict`` with an
            ``"id"`` or ``"fingerprint"`` field, or an `SSHKey` object (to
            re-fetch the same SSH key)
        :type obj: integer, string, ``dict``, or `SSHKey`
        :rtype: SSHKey
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.ssh_key(obj).fetch()

    def fetch_all_ssh_keys(self):
        """
        Returns a generator that yields all of the SSH public keys belonging to
        the account in the order that the API endpoint returns them

        :rtype: generator of `SSHKey`s
        """
        return map(self.ssh_key, self.paginate('/v2/account/keys', 'ssh_keys'))

    def create_ssh_key(self, name, public_key):
        """
        Adds a new SSH public key resource to the account

        :param str name: the name to give the new SSH key resource
        :param str public_key: the text of the public key to register, in the
            form used by ``authorized_keys`` files
        :return: the new SSH key resource
        :rtype: SSHKey
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.ssh_key(self.request('/v2/account/keys', method='POST',
                                         data={
                                             "name": name,
                                             "public_key": public_key
                                         })["ssh_key"])

    def image(self, obj):
        """
        Constructs an `Image` object belonging to the `doapi` object.  ``obj``
        may be an image ID, a dictionary of image fields, or another `Image`
        object (which will be shallow-copied).  The resulting `Image` will only
        contain the information in ``obj``; no data will be sent to or from the
        API endpoint.

        :type obj: integer, ``dict``, or `Image`
        :rtype: Image
        """
        return Image(obj, doapi_manager=self)

    def fetch_image(self, obj):
        """
        Fetches an image by ID number

        :param obj: the ID of the image, a ``dict`` with an ``"id"`` field, or
            an `Image` object (to re-fetch the same image)
        :type obj: integer, ``dict``, or `Image`
        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.image(obj).fetch()

    def fetch_image_by_slug(self, slug):
        """
        Fetches an image by its slug

        :param str slug: the slug of the image to fetch
        :rtype: Image
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.image(self.request('/v2/images/' + slug)["image"])

    def fetch_all_images(self, type=None, private=False):
        """
        Returns a generator that yields all of the images available to the
        account in the order that the API endpoint returns them

        :param type: the type of images to fetch: ``"distribution"``,
            ``"application"``, or all (``None``); default: ``None``
        :type type: string or None
        :param bool private: whether to only return the user's private images;
            default: ``False`` (i.e., return all images)
        :rtype: generator of `Image`s
        """
        params = {}
        if type is not None:
            params["type"] = type
        if private:
            params["private"] = 'true'
        return map(self.image, self.paginate('/v2/images', 'images',
                                             params=params))

    def fetch_all_distribution_images(self):
        """
        Returns a generator that yields all of the distribution images
        available to the account in the order that the API endpoint returns
        them

        :rtype: generator of `Image`s
        """
        return self.fetch_all_images(type='distribution')

    def fetch_all_application_images(self):
        """
        Returns a generator that yields all of the application images available
        to the account in the order that the API endpoint returns them

        :rtype: generator of `Image`s
        """
        return self.fetch_all_images(type='application')

    def fetch_all_private_images(self):
        """
        Returns a generator that yields all of the user's private images in the
        order that the API endpoint returns them

        :rtype: generator of `Image`s
        """
        return self.fetch_all_images(private=True)

    def region(self, obj):
        """
        Constructs a `Region` object belonging to the `doapi` object.  ``obj``
        may be a dictionary of region fields or another `Region` object (which
        will be shallow-copied).  The resulting `Region` will only contain the
        information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: ``dict`` or `Region`
        :rtype: Region
        """
        return Region(obj, doapi_manager=self)

    def fetch_all_regions(self):
        """
        Returns a generator that yields all of the regions available to the
        account in the order that the API endpoint returns them

        :rtype: generator of `Region`s
        """
        return map(self.region, self.paginate('/v2/regions', 'regions'))

    def size(self, obj):
        """
        Constructs a `Size` object belonging to the `doapi` object.  ``obj``
        may be a dictionary of size fields or another `Size` object (which will
        be shallow-copied).  The resulting `Size` will only contain the
        information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: ``dict`` or `Size`
        :rtype: Size
        """
        return Size(obj, doapi_manager=self)

    def fetch_all_sizes(self):
        """
        Returns a generator that yields all of the sizes available to the
        account in the order that the API endpoint returns them

        :rtype: generator of `Size`s
        """
        return map(self.size, self.paginate('/v2/sizes', 'sizes'))

    def fetch_account(self):
        """
        Returns an `Account` object representing the user's account

        :rtype: Account
        """
        return Account(self.request('/v2/account')["account"],
                       doapi_manager=self)

    def domain(self, obj):
        """
        Constructs a `Domain` object belonging to the `doapi` object.  ``obj``
        may be a domain name, a dictionary of domain fields, or another
        `Domain` object (which will be shallow-copied).  The resulting `Domain`
        will only contain the information in ``obj``; no data will be sent to
        or from the API endpoint.

        :type obj: string, ``dict``, or `Domain`
        :rtype: Domain
        """
        return Domain(obj, doapi_manager=self)

    def fetch_domain(self, obj):
        """
        Fetches a domain by FQDN

        :param obj: the domain name, a ``dict`` with a ``"name"`` field, or a
            `Domain` object (to re-fetch the same domain)
        :type obj: string, ``dict``, or `Domain`
        :rtype: Domain
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.domain(obj).fetch()

    def fetch_all_domains(self):
        """
        Returns a generator that yields all of the domains belonging to the
        account in the order that the API endpoint returns them

        :rtype: generator of `Domain`s
        """
        return map(self.domain, self.paginate('/v2/domains', 'domains'))

    def create_domain(self, name, ip_address):
        """
        Adds a new domain name resource to the account

        :param str name: the domain name to add
        :param str ip_address: the IP address to which the domain should point
        :return: the new domain resource
        :rtype: Domain
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.domain(self.request('/v2/domains', method='POST', data={
            "name": name,
            "ip_address": ip_address,
        })["domain"])

    def floating_ip(self, obj):
        """
        Constructs a `FloatingIP` object belonging to the `doapi` object.
        ``obj`` may be an IP address (as a string or 32-bit integer), a
        dictionary of floating IP fields, or another `FloatingIP` object (which
        will be shallow-copied).  The resulting `FloatingIP` will only contain
        the information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: string, integer, ``dict``, or `FloatingIP`
        :rtype: FloatingIP
        """
        return FloatingIP(obj, doapi_manager=self)

    def fetch_floating_ip(self, obj):
        """
        Fetches a floating IP

        :param obj: an IP address (as a string or 32-bit integer), a ``dict``
            with an ``"ip"`` field, or a `FloatingIP` object (to re-fetch the
            same floating IP)
        :type obj: string, integer, ``dict``, or `FloatingIP`
        :rtype: FloatingIP
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.floating_ip(obj).fetch()

    def fetch_all_floating_ips(self):
        """
        Returns a generator that yields all of the floating IPs belonging to
        the account in the order that the API endpoint returns them

        :rtype: generator of `FloatingIP`s
        """
        return map(self.floating_ip, self.paginate('/v2/floating_ips',
                                                   'floating_ips'))

    def create_floating_ip(self, droplet_id=None, region=None):
        """
        Creates a new floating IP assigned to a droplet or reserved to a
        region.  Either ``droplet_id`` or ``region`` must be specified, but not
        both.

        :param droplet_id: the droplet to assign the floating IP to as either
            an ID or a `Droplet` object
        :type droplet_id: integer or `Droplet`
        :param region: the region to reserve the floating IP to as either a
            slug or a `Region` object
        :type region: string or `Region`
        :return: the new floating IP
        :rtype: FloatingIP
        :raises TypeError: if both ``droplet_id`` & ``region`` or neither of
            them are defined
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if (droplet_id is None) == (region is None):
            ### Is TypeError the right type of error?
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
        return self.floating_ip(self.request('/v2/floating_ips', method='POST',
                                             data=data)["floating_ip"])

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)

    def _wait(self, objects, isdone, wait_interval=None, wait_time=None):
        """
        Calls the ``fetch`` method of each object in ``objects`` periodically
        until ``isdone`` returns true on each one, yielding the final value of
        each object as soon as it succeeds.  If ``wait_time`` is exceeded or a
        ``KeyboardInterrupt`` is caught, any remaining objects are returned
        immediately without waiting for completion.

        :param iterable objects: an iterable of objects with ``fetch`` methods
            (presumably `JSObject`s)
        :param number wait_interval: how many seconds to sleep between
            requests; defaults to :attr:`wait_interval` if not specified or
            ``None``
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to :attr:`wait_time` if not specified or ``None``
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
            try:
                if end_time is None:
                    sleep(wait_interval)
                else:
                    sleep(min(wait_interval, end_time - time()))
            except KeyboardInterrupt:
                break
        for o in objects:
            yield o
