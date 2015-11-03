from six.moves import map
from .base     import JSObject, JSObjectWithID

class Domain(JSObject):
    def __init__(self, state=None, **extra):
        if isinstance(state, basestring):
            state = {"name": state}
        super(Domain, self).__init__(state, **extra)

    def __str__(self):
        return self.name

    @property
    def url(self):
        return self._url('/v2/domains/' + self.name)

    def fetch(self):
        api = self.doapi_manager
        return api.domain(api.request(self.url)["domain"])

    def delete(self):
        self.doapi_manager.request(self.url, method='DELETE')

    def record(self, obj):
        return DomainRecord(obj, domain=self, doapi_manager=self.doapi_manager)

    @property
    def record_url(self):
        return self.url + '/records'

    def fetch_record(self, obj):
        return self.record(obj).fetch()

    def fetch_all_records(self):
        api = self.doapi_manager
        return map(self.record, api.paginate(self.record_url, 'domain_records'))

    def create_record(self, type, name, data, priority=None, port=None,
                      weight=None):
        return self.record(self.request(self.record_url, method='POST', data={
            "type": type,
            "name": name,
            "data": data,
            "priority": priority,
            "port": port,
            "weight": weight,
        })["domain_record"])


class DomainRecord(JSObjectWithID):
    _meta_attrs = JSObjectWithID._meta_attrs + ('domain',)

    @property
    def url(self):
        return self.domain.record_url + '/' + str(self.id)

    def fetch(self):
        return self.domain.record(self.doapi_manager.request(self.url)\
                                                            ["domain_record"])

    def fetch_domain(self):
        return self.domain.fetch()

    def update_record(self, **attrs):
        # The `_record` is to avoid conflicts with MutableMapping.update.
        return self.domain.record(self.doapi_manager.request(self.url,
                                                             method='PUT',
                                                             data=attrs)\
                                                            ["domain_record"])

    def delete(self):
        self.doapi_manager.request(self.url, method='DELETE')
