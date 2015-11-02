import numbers
import socket
import struct
from   urlparse import urljoin
from   .base    import Actionable, Region
from   .droplet import Droplet

class FloatingIP(Actionable):
    def __init__(self, state=None, **extra):
        if isinstance(state, numbers.Integral):
            state = {"ip": socket.inet_ntoa(struct.pack('!I', state))}
        elif isinstance(state, basestring):
            state = {"ip": state}
        super(FloatingIP, self).__init__(state, **extra)
        for attr, cls in [('region', Region), ('droplet', Droplet)]:
            if self.get(attr) is not None and not isinstance(self[attr], cls):
                self[attr] = cls(self[attr], doapi_manager=self.doapi_manager)

    def __str__(self):
        return self.ip

    def url(self, endpoint=''):
        return urljoin(endpoint, '/v2/floating_ips/' + self.ip)

    def action_url(self, endpoint=''):
        return urljoin(endpoint, '/v2/floating_ips/' + self.ip + '/actions')

    def fetch(self):
        api = self.doapi_manager
        return api.floating_ip(api.request(self.url())["floating_ip"])

    def delete(self):
        self.doapi_manager.request(self.url(), method='DELETE')

    def assign(self, droplet_id):
        if isinstance(droplet_id, Droplet):
            droplet_id = droplet_id.id
        return self.act(type='assign', droplet_id=droplet_id)

    def unassign(self):
        return self.act(type='unassign')
