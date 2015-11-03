from urlparse  import urljoin
from six.moves import map
from .base     import Actionable, JSObjectWithID, Region, Size, Kernel, Networks
from .image    import Image

class Droplet(Actionable, JSObjectWithID):
    def __init__(self, state=None, **extra):
        super(Droplet, self).__init__(state, **extra)
        for attr, cls in [('image', Image), ('region', Region), ('size', Size),
                          ('kernel', Kernel), ('networks', Networks)]:
            if self.get(attr) is not None and not isinstance(self[attr], cls):
                self[attr] = cls(self[attr], doapi_manager=self.doapi_manager)
                if attr in ('kernel', 'networks', 'image'):
                    self[attr].droplet = self

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
        v4nets = self.networks.get("v4", [])
        v6nets = self.networks.get("v6", [])
        try:
            return (v4nets + v6nets)[0].ip_address
        except IndexError:
            return None

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/droplets/' + str(self.id))

    def action_url(self, endpoint=''):
        return urljoin(endpoint, '/v2/droplets/' + str(self.id) + '/actions')

    def disable_backups(self):
        return self.act(type='disable_backups')

    def reboot(self):
        return self.act(type='reboot')

    def power_cycle(self):
        return self.act(type='power_cycle')

    def shutdown(self):
        return self.act(type='shutdown')

    def power_off(self):
        return self.act(type='power_off')

    def power_on(self):
        return self.act(type='power_on')

    def restore(self, image):
        if isinstance(image, Image):
            image = image.id
        return self.act(type='restore', image=image)

    def password_reset(self):
        return self.act(type='password_reset')

    def resize(self, size, disk=None):
        if isinstance(size, Size):
            size = size.slug
        opts = {"disk": disk} if disk is not None else {}
        return self.act(type='resize', size=size, **opts)

    def rebuild(self, image):
        if isinstance(image, Image):
            image = image.id
        return self.act(type='rebuild', image=image)

    def rename(self, name):
        return self.act(type='rename', name=name)

    def change_kernel(self, kernel):
        if isinstance(kernel, Kernel):
            kernel = kernel.id
        return self.act(type='change_kernel', kernel=kernel)

    def enable_ipv6(self):
        return self.act(type='enable_ipv6')

    def enable_private_networking(self):
        return self.act(type='enable_private_networking')

    def snapshot(self, name):
        return self.act(type='snapshot', name=name)

    def upgrade(self):
        return self.act(type='upgrade')

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')

    def fetch(self):
        api = self.doapi_manager
        return api.droplet(api.request(self.url())["droplet"])

    def fetch_all_neighbors(self):
        api = self.doapi_manager
        return map(api.droplet, api.paginate(self.url() + '/neighbors',
                                             'droplets'))

    def fetch_all_snapshots(self):
        api = self.doapi_manager
        for obj in api.paginate(self.url() + '/snapshots', 'snapshots'):
            yield Image(obj, doapi_manager=api, droplet=self)

    def fetch_all_backups(self):
        api = self.doapi_manager
        for obj in api.paginate(self.url() + '/backups', 'backups'):
            yield Image(obj, doapi_manager=api, droplet=self)

    def fetch_all_kernels(self):
        api = self.doapi_manager
        for kern in api.paginate(self.url() + '/kernels', 'kernels'):
            yield Kernel(kern, doapi_manager=api, droplet=self)

    def wait(self, status=None, wait_interval=None, wait_time=None):
        return next(self.doapi_manager.wait_droplets([self], status,
                                                     wait_interval, wait_time))
