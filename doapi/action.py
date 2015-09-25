from urlparse import urljoin
from .base    import JSObject

class Action(JSObject):
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
        api = self.doapi_manager
        return api.action(api.request(self.url())["action"])

    def fetch_resource(self):
        if self.resource_type == "droplet":
            return self.doapi_manager.fetch_droplet(self.resource_id)
        elif self.resource_type == "image":
            return self.doapi_manager.fetch_image(self.resource_id)
        else:
            raise ValueError('Unknown resource_type: ' + repr(self.resource_type))

    def wait(self, interval=None, maxwait=-1):
        if interval is None:
            interval = self.doapi_manager.wait_interval
        end_time = time() + maxwait if maxwait > 0 else None
        current = self
        while end_time is None or time() < end_time:
            current = current.fetch()
            if current.done:
                return current
            if end_time is None:
                sleep(interval)
            else:
                sleep(min(interval, end_time - time()))
