from time     import sleep, time
from urlparse import urljoin
from .base    import JSObject, Region, Size, Kernel, Networks
from .image   import Image

class Droplet(JSObject):
    def __init__(self, state={}, **extra):
        super(Droplet, self).__init__(state, **extra)
        try:
            meta = {"doapi_manager": self.doapi_manager}
        except AttributeError:
            meta = {}
        for attr, cls in [('image', Image), ('region', Region), ('size', Size),
                          ('kernel', Kernel), ('networks', Networks)]:
            if getattr(self, attr, None) is not None:
                if attr in ('kernel', 'networks'):   ### also 'image'?
                    new = cls(getattr(self, attr), droplet=self, **meta)
                else:
                    new = cls(getattr(self, attr), **meta)
                setattr(self, attr, new)

    def __int__(self):
        return self.id

    @property
    def active(self):
        return self.status == 'active'

    @property
    def new(self):
        return self.status == 'new'

    @property
    def off(self):
        return self.status == 'off'

    @property
    def archive(self):
        return self.status == 'archive'

    @property
    def region_slug(self):
        return self.region.slug

    @property
    def image_slug(self):
        return self.image.slug

    @property
    def ip_address(self):
        v4nets = getattr(self.networks, "v4", [])
        v6nets = getattr(self.networks, "v6", [])
        try:
            return (v4nets + v6nets)[0].ip_address
        except IndexError:
            return None

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/droplets/' + str(self.id))

    def action_url(self, endpoint=''):
        return urljoin(endpoint, '/v2/droplets/' + str(self.id) + '/actions')

    def action(self, **data):  ### TODO: Rethink name; `act`?
        api = self.doapi_manager
        return api.action(api.request(self.action_url(), method='POST',
                                      data=data)["action"])

    def disable_backups(self):
        return self.action(type='disable_backups')

    def reboot(self):
        return self.action(type='reboot')

    def power_cycle(self):
        return self.action(type='power_cycle')

    def shutdown(self):
        return self.action(type='shutdown')

    def power_off(self):
        return self.action(type='power_off')

    def power_on(self):
        return self.action(type='power_on')

    def restore(self, image):
        return self.action(type='restore', image=image)

    def password_reset(self):
        return self.action(type='password_reset')

    def resize(self, size, disk=None):
        opts = {"disk": disk} if disk is not None else {}
        return self.action(type='resize', size=size, **opts)

    def rebuild(self, image):
        return self.action(type='rebuild', image=image)

    def rename(self, name):
        return self.action(type='rename', name=name)

    def change_kernel(self, kernel):
        return self.action(type='change_kernel', kernel=kernel)

    def enable_ipv6(self):
        return self.action(type='enable_ipv6')

    def enable_private_networking(self):
        return self.action(type='enable_private_networking')

    def snapshot(self, name):
        return self.action(type='snapshot', name=name)

    def upgrade(self):
        return self.action(type='upgrade')

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')

    def fetch(self):
        api = self.doapi_manager
        return api.droplet(api.request(self.url())["droplet"])

    def fetch_all_neighbors(self):
        api = self.doapi_manager
        return map(api.droplet, api.paginate(self.url() + '/neighbors',
                                             'droplets'))

    def fetch_all_actions(self):
        api = self.doapi_manager
        return map(api.action, api.paginate(self.action_url(), 'actions'))

    def wait(self, status=None, interval=None, maxwait=-1):
        if status is None:
            self.fetch_last_action().wait(interval=interval, maxwait=maxwait)
            ### TODO: Should this do something if the action errored?
            return self.fetch()
        else:
            if interval is None:
                interval = self.doapi_manager.wait_interval
            end_time = time() + maxwait if maxwait > 0 else None
            current = self
            while end_time is None or time() < end_time:
                current = current.fetch()
                if current.status == status:
                    return current
                if end_time is None:
                    sleep(interval)
                else:
                    sleep(min(interval, end_time - time()))

    def fetch_last_action(self):
        # Naive implementation:
        api = self.doapi_manager
        return api.action(api.request(self.action_url())["actions"][0])
        """
        # Slow yet guaranteed-correct implementation:
        return max(self.fetch_all_actions(), key=lambda a: a.started_at)
        """

    def fetch_all_snapshots(self):
        api = self.doapi_manager
        return [Image(obj, doapi_manager=api, droplet=self)
                for obj in api.paginate(self.url() + '/snapshots', 'snapshots')]

    def fetch_all_backups(self):
        api = self.doapi_manager
        return [Image(obj, doapi_manager=api, droplet=self)
                for obj in api.paginate(self.url() + '/backups', 'backups')]

    def fetch_all_kernels(self):
        api = self.doapi_manager
        return [Kernel(kern, doapi_manager=api, droplet=self)
                for kern in api.paginate(self.url() + '/kernels', 'kernels')]
