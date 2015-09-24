from urlparse import urljoin

class Droplet(JSObject):
    def __init__(self, state):
        if isinstance(state, Droplet):
            state = vars(state)
        try:
            api = state["doapi_manager"]
        except KeyError:
            mkimage, mkregion, mksize = Image, Region, Size
        else:
            mkimage, mkregion, mksize = api.image, api.region, api.size
        if "image" in state:
            state["image"] = mkimage(state["image"])
        if "region" in state:
            state["region"] = mkregion(state["region"])
        if "size" in state:
            state["size"] = mksize(state["size"])
        super(Droplet, self).__init__(state)

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
        try:
            ### TODO: Are v4 and v6 both present right after a droplet is
            ### created?
            return (self.networks["v4"] + self.networks["v6"])[0]["ip_address"]
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

    def fetch_neighbors(self):
        api = self.doapi_manager
        # Yes, that's really supposed to be a literal backslash in the URL.
        return map(api.droplet, api.paginate(self.url() + r'\neighbors',
                                             'droplets'))

    def fetch(self):
        return self.doapi_manager.fetch_droplet(int(self))

    def fetch_actions(self):
        api = self.doapi_manager
        return map(api.action, api.paginate(self.action_url(), 'actions'))

    ### def wait(self, status=None)
    # When `status is None`, wait for most recent action to complete/error

    ### fetch_kernels
    ### fetch_snapshots
    ### fetch_backups
