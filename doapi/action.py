from .base import JSObjectWithID, DOAPIError

class Action(JSObjectWithID):
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

    @property
    def url(self):
        ### TODO: Look into the conditions under which this has to include the
        ### resource type & ID too
        return self._url('/v2/actions/' + str(self.id))

    def fetch(self):
        api = self.doapi_manager
        return api.action(api.request(self.url)["action"])

    def fetch_resource(self):
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
        return next(self.doapi_manager.wait_actions([self], wait_interval,
                                                            wait_time))
