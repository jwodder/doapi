from six       import string_types
from six.moves import map  # pylint: disable=redefined-builtin
from .base     import Resource, ResourceWithID

class Domain(Resource):
    """
    A domain resource, representing a domain name whose DNS is managed by
    DigitalOcean's nameservers.

    New domains are created via the :meth:`doapi.create_domain` method and can
    be retrieved with the :meth:`doapi.fetch_domain` and
    :meth:`doapi.fetch_all_domains` methods.

    The DigitalOcean API specifies the following fields for domain objects:

    :var name: the domain name
    :vartype name: string

    :var ttl: the time-to-live for the domain's records, in seconds
    :vartype ttl: number

    :var zone_file: the complete zone file for the domain
    :vartype zone_file: string
    """

    def __init__(self, state=None, **extra):
        if isinstance(state, string_types):
            state = {"name": state}
        super(Domain, self).__init__(state, **extra)

    def __str__(self):
        """ Convert the domain to just the actual domain name """
        return self.name

    @property
    def url(self):
        """ The endpoint for operations on the specific domain """
        return self._url('/v2/domains/' + self.name)

    def fetch(self):
        """
        Fetch & return a new `Domain` object representing the domain's current
        state

        :rtype: Domain
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the domain no longer exists)
        """
        api = self.doapi_manager
        return api._domain(api.request(self.url)["domain"])

    def delete(self):
        """
        Delete the domain

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')

    def _record(self, obj):
        """
        Construct a `DomainRecord` object belonging to the domain's `doapi`
        object.  ``obj`` may be a domain record ID, a dictionary of domain
        record fields, or another `DomainRecord` object (which will be
        shallow-copied).  The resulting `DomainRecord` will only contain the
        information in ``obj``; no data will be sent to or from the API
        endpoint.

        :type obj: integer, `dict`, or `DomainRecord`
        :rtype: DomainRecord
        """
        return DomainRecord(obj, domain=self, doapi_manager=self.doapi_manager)

    @property
    def record_url(self):
        """ The endpoint for operations on the domain's DNS records """
        return self.url + '/records'

    def fetch_record(self, obj):
        """
        Fetch a domain record by ID number

        :param obj: the ID of the record, a `dict` with an ``"id"`` field,
            or a `DomainRecord` object (to re-fetch the same record)
        :type obj: integer, `dict`, or `DomainRecord`
        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._record(obj).fetch()

    def fetch_all_records(self):
        r"""
        Returns a generator that yields all of the DNS records for the domain

        :rtype: generator of `DomainRecord`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return map(self._record, api.paginate(self.record_url, 'domain_records'))

    def create_record(self, type, name, data, priority=None, port=None,
                      weight=None, **kwargs):
        """
        Add a new DNS record to the domain

        :param str type: the type of DNS record to add (``"A"``, ``"CNAME"``,
            etc.)
        :param str name: the name (hostname, alias, etc.) of the new record
        :param str data: the value of the new record
        :param int priority: the priority of the new record (SRV and MX records
            only)
        :param int port: the port that the service is accessible on (SRV
            records only)
        :param int weight: the weight of records with the same priority (SRV
            records only)
        :param kwargs: additional fields to include in the API request
        :return: the new domain record
        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        data = {
            "type": type,
            "name": name,
            "data": data,
            "priority": priority,
            "port": port,
            "weight": weight,
        }
        data.update(kwargs)
        return self._record(api.request(self.record_url, method='POST',
                                        data=data)["domain_record"])


class DomainRecord(ResourceWithID):
    """
    A domain record resource, representing an individual DNS record that can be
    set & modified by the user of the DigitalOcean API.

    New domain records are created via the :meth:`Domain.create_record` method
    and can be retrieved with the :meth:`Domain.fetch_record` and
    :meth:`Domain.fetch_all_records` methods.

    The DigitalOcean API specifies the following fields for domain record
    objects:

    :var id: a unique identifier for the domain record
    :vartype id: int

    :var type: the type of the DNS record
    :vartype type: string

    :var name: the name of the DNS record
    :vartype name: string

    :var data: the value of the DNS record
    :vartype data: string

    :var priority: the priority of the record (SRV and MX records only)
    :vartype priority: number or `None`

    :var port: the port of the record (SRV records only)
    :vartype port: number or `None`

    :var weight: the weight of the record (SRV records only)
    :vartype weight: number or `None`

    .. attribute:: domain

       The `Domain` to which the record belongs
    """

    _meta_attrs = ResourceWithID._meta_attrs + ('domain',)

    @property
    def url(self):
        """ The endpoint for operations on the specific domain record """
        return self.domain.record_url + '/' + str(self.id)

    def fetch(self):
        """
        Fetch & return a new `DomainRecord` object representing the domain
        record's current state

        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the domain record no longer exists)
        """
        return self.domain._record(self.doapi_manager.request(self.url)\
                                                             ["domain_record"])

    def fetch_domain(self):
        """
        Fetch & return the domain resource that the record belongs to

        :rtype: Domain
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.domain.fetch()

    def update_record(self, **attrs):
        # The `_record` is to avoid conflicts with MutableMapping.update.
        """
        Update the record, modifying any number of its attributes (except
        ``id``).  ``update_record`` takes the same keyword arguments as
        :meth:`Domain.create_record`; pass in only those attributes that you
        want to update.

        :return: an updated `DomainRecord` object
        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.domain._record(self.doapi_manager.request(self.url,
                                                              method='PUT',
                                                              data=attrs)\
                                                             ["domain_record"])

    def delete(self):
        """
        Delete the domain record

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')
