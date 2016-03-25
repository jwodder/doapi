import numbers
import socket
import struct
from   six      import string_types
from   .base    import Actionable, Region
from   .droplet import Droplet

class FloatingIP(Actionable):
    """
    A floating IP resource, representing a public IP address that can be
    (re)assigned at any time to any droplet in a certain region.

    New floating IPs are created via the :meth:`doapi.create_floating_ip`
    method and can be retrieved with the :meth:`doapi.fetch_floating_ip` and
    :meth:`doapi.fetch_all_floating_ips` methods.

    The DigitalOcean API specifies the following fields for floating IP
    objects:

    :var ip: the IP address
    :vartype ip: string

    :var droplet: the droplet the floating IP is currently assigned to, or
        `None` if the address is currently unassigned
    :vartype droplet: `Droplet` or `None`

    :var region: the region the floating IP is reserved to
    :vartype region: `Region`
    """

    def __init__(self, state=None, **extra):
        if isinstance(state, numbers.Integral):
            state = {"ip": socket.inet_ntoa(struct.pack('!I', state))}
        elif isinstance(state, string_types):
            state = {"ip": state}
        super(FloatingIP, self).__init__(state, **extra)
        for attr, cls in [('region', Region), ('droplet', Droplet)]:
            if self.get(attr) is not None and not isinstance(self[attr], cls):
                self[attr] = cls(self[attr], doapi_manager=self.doapi_manager)

    def __str__(self):
        """ Convert the floating IP to just the actual IP address """
        return self.ip

    @property
    def url(self):
        """ The endpoint for operations on the specific floating IP """
        return self._url('/v2/floating_ips/' + self.ip)

    def fetch(self):
        """
        Fetch & return a new `FloatingIP` object representing the floating IP's
        current state

        :rtype: FloatingIP
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the floating IP no longer exists)
        """
        api = self.doapi_manager
        return api._floating_ip(api.request(self.url)["floating_ip"])

    def delete(self):
        """
        Delete the floating IP

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')

    def assign(self, droplet_id):
        """
        Assign the floating IP to a droplet

        :param droplet_id: the droplet to assign the floating IP to as either
            an ID or a `Droplet` object
        :type droplet_id: integer or `Droplet`
        :return: an `Action` representing the in-progress operation on the
            floating IP
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if isinstance(droplet_id, Droplet):
            droplet_id = droplet_id.id
        return self.act(type='assign', droplet_id=droplet_id)

    def unassign(self):
        """
        Unassign the floating IP

        :return: an `Action` representing the in-progress operation on the
            floating IP
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='unassign')
