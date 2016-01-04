from six       import string_types
from six.moves import map
from .base     import Resource, ResourceWithID

class Domain(Resource):
    """
    TODO

    [Mention that passing another Domain's DomainRecord to a Domain results in
    undefined behavior.]
    """

    def __init__(self, state=None, **extra):
        """ TODO """
        if isinstance(state, string_types):
            state = {"name": state}
        super(Domain, self).__init__(state, **extra)

    def __str__(self):
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

        :rtype: None
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

        :type obj: integer, ``dict``, or `DomainRecord`
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

        :param obj: the ID of the record, a ``dict`` with an ``"id"`` field,
            or a `DomainRecord` object (to re-fetch the same record)
        :type obj: integer, ``dict``, or `DomainRecord`
        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._record(obj).fetch()

    def fetch_all_records(self):
        r"""
        Returns a generator that yields all of the DNS records for the domain

        :rtype: generator of `DomainRecord`\ s
        """
        api = self.doapi_manager
        return map(self._record, api.paginate(self.record_url, 'domain_records'))

    def create_record(self, type, name, data, priority=None, port=None,
                      weight=None):
        """
        Add a new DNS record to the domain

        :param str type: the type of DNS record to add (``"A"``, ``"CNAME"``,
            etc.)
        :param str name: the name (hostname, alias, etc.) of the new record
        :param str data: the value of the new record
        :param number priority: the priority of the new record (SRV and MX
            records only)
        :param number port: the port that the service is accessible on (SRV
            records only)
        :param number weight: the weight of records with the same priority (SRV
            records only)
        :return: the new domain record
        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return self._record(api.request(self.record_url, method='POST', data={
            "type": type,
            "name": name,
            "data": data,
            "priority": priority,
            "port": port,
            "weight": weight,
        })["domain_record"])


class DomainRecord(ResourceWithID):
    """ TODO """

    _meta_attrs = ResourceWithID._meta_attrs + ('domain',)

    @property
    def url(self):
        """ The endpoint for operations on the specific domain record """
        return self._domain.record_url + '/' + str(self.id)

    def fetch(self):
        """
        Fetch & return a new `DomainRecord` object representing the domain
        record's current state

        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the domain record no longer exists)
        """
        return self._domain._record(self.doapi_manager.request(self.url)\
                                                              ["domain_record"])

    def fetch_domain(self):
        """
        Fetch & return the domain resource that the record belongs to

        :rtype: Domain
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._domain.fetch()

    def update_record(self, **attrs):
        # The `_record` is to avoid conflicts with MutableMapping.update.
        """
        Update the record, modifying any number of its attributes.
        ``update_record`` takes the same keyword arguments as
        :meth:`Domain.create_record`; pass in only those attributes that you
        want to update.

        :return: an updated `DomainRecord` object
        :rtype: DomainRecord
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self._domain._record(self.doapi_manager.request(self.url,
                                                               method='PUT',
                                                               data=attrs)\
                                                              ["domain_record"])

    def delete(self):
        """
        Delete the domain record

        :rtype: None
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')
