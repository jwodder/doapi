from urlparse import urljoin
from .base    import JSObject

class Domain(JSObject):
    def __init__(self, state={}, **extra):
        if isinstance(state, basestring):
            state = {"name": state}
        super(Domain, self).__init__(state, **extra)

    def __str__(self):
        return self.name

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/domains/' + self.name)

    def fetch(self):
        api = self.doapi_manager
        return api.domain(api.request(self.url())["domain"])

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')

    def record(self, obj):
        ### Handle `self.doapi_manager` not existing
        return DomainRecord(obj, doapi_manager=self.doapi_manager, domain=self)

    def record_url(self, endpoint=''):
        return urljoin(endpoint, self.url() + '/records')

    def fetch_record(self, obj):
        return self.record(obj).fetch()

    def fetch_all_records(self):
        api = self.doapi_manager
        return map(self.record, api.paginate(self.record_url(),
                                             'domain_records'))

    def create_record(self, type, name, data, priority=None, port=None,
                      weight=None):
        return self.record(self.request(self.record_url(), method='POST', data={
            "type": type,
            "name": name,
            "data": data,
            "priority": priority,
            "port": port,
            "weight": weight,
        })["domain_record"])


class DomainRecord(JSObject):
    _meta_attrs = JSObject._meta_attrs + ('domain',)

    ### Should this try to handle self.domain being a string?

    def __int__(self):
        return self.id

    def url(self):
        return urljoin(endpoint, self.domain.record_url() + '/' + str(self.id))

    def fetch(self):
        return self.domain.record(self.doapi_manager.request(self.url())["domain_record"])

    ### Rethink the arguments:
    def update(self, **attrs):
        return self.domain.record(self.doapi_manager.request(self.url(), method='PUT', data=attrs)["domain_record"])

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')
