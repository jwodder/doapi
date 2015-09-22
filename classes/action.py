from urlparse import urljoin

class Action(JSObject):
    __slots__ = ()

    def __int__(self):
        return self.id

    @property
    def completed(self):
        return self.status == 'completed'

    @property
    def in_progress(self):
        return self.status == 'in-progress'

    @property
    def done(self):
        return self.status != 'in-progress'

    @property
    def errored(self):
        return self.status == 'errored'

    def url(self, endpoint=''):
        ### TODO: Look into the conditions under which this has to include the
        ### resource type & ID too
        return urljoin(endpoint, '/v2/actions/' + str(self.id))

    def fetch(self):
        return self.doapi_manager.fetch_action(int(self))
