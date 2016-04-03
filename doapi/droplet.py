from datetime  import datetime
from six.moves import map  # pylint: disable=redefined-builtin
from .base     import Actionable, ResourceWithID, Region, Size, Kernel, \
                        Networks, BackupWindow, ResourceWithDroplet, fromISO8601
from .image    import Image

class Droplet(Actionable, ResourceWithID):
    """
    A droplet resource, representing a virtual machine provided by
    DigitalOcean.

    New droplets are created via the :meth:`doapi.create_droplet` and
    :meth:`doapi.create_multiple_droplets` methods and can be retrieved with
    the :meth:`doapi.fetch_droplet` and :meth:`doapi.fetch_all_droplets`
    methods.

    The DigitalOcean API specifies the following fields for droplet objects:

    :var id: a unique identifier for the droplet
    :vartype id: int

    :var backup_ids: image IDs of backups taken of the droplet
    :vartype backup_ids: list of integers

    :var created_at: date & time of the droplet's creation
    :vartype created_at: datetime.datetime

    :var disk: size of the droplet's disk in gigabytes
    :vartype disk: number

    :var features: a list of strings naming the features enabled on the droplet
    :vartype features: list of strings

    :var image: the base image used to create the droplet
    :vartype image: `Image`

    :var kernel: the droplet's current kernel
    :vartype kernel: `Kernel` or `None`

    :var locked: whether the droplet is currently locked, preventing actions on
        it
    :vartype locked: bool

    :var memory: RAM of the droplet in megabytes
    :vartype memory: number

    :var name: a human-readable name for the droplet
    :vartype name: string

    :var networks: the network interfaces configured for the droplet
    :vartype networks: `Networks`

    :var next_backup_window: the start & end of the next timeframe in which the
        droplet will be backed up; only defined if backups are enabled on the
        droplet
    :vartype next_backup_window: `BackupWindow` or `None`

    :var region: the region in which the droplet is located
    :vartype region: `Region`

    :var size: the current size of the droplet
    :vartype size: `Size`

    :var size_slug: the unique slug identifier for the droplet's size
    :vartype size_slug: string

    :var snapshot_ids: image IDs of snapshots taken of the droplet
    :vartype snapshot_ids: list of integers

    :var status: the current state of the droplet: ``"new"``, ``"active"``,
        ``"off"``, or ``"archive"``
    :vartype status: string

    :var vcpus: number of virtual CPUs
    :vartype vcpus: int
    """

    #: The status of droplets that are powered on and operating
    STATUS_ACTIVE = 'active'

    #: The status of "archived" droplets
    STATUS_ARCHIVE = 'archive'

    #: The status of recently-created droplets that are not yet usable
    STATUS_NEW = 'new'

    #: The status of droplets that are powered off
    STATUS_OFF = 'off'

    def __init__(self, state=None, **extra):
        super(Droplet, self).__init__(state, **extra)
        for attr, cls in [('image', Image), ('region', Region), ('size', Size),
                          ('kernel', Kernel), ('networks', Networks),
                          ('next_backup_window', BackupWindow)]:
            if self.get(attr) is not None and not isinstance(self[attr], cls):
                extra = {}
                if isinstance(cls, ResourceWithDroplet):
                    extra = {"droplet": self}
                    # `droplet` needs to be set when creating the objects so
                    # that the `Networks` object will pass the value to its
                    # `NetworkInterface`s.
                self[attr] = cls(self[attr], doapi_manager=self.doapi_manager,
                                 **extra)
        if self.get('created_at') is not None and \
                not isinstance(self.created_at, datetime):
            self.created_at = fromISO8601(self.created_at)

    @property
    def active(self):
        """ `True` iff the droplet's status is ``"active"`` """
        return self.status == self.STATUS_ACTIVE

    @property
    def new(self):
        """ `True` iff the droplet's status is ``"new"`` """
        return self.status == self.STATUS_NEW

    @property
    def off(self):
        """ `True` iff the droplet's status is ``"off"`` """
        return self.status == self.STATUS_OFF

    @property
    def archive(self):
        """ `True` iff the droplet's status is ``"archive"`` """
        return self.status == self.STATUS_ARCHIVE

    @property
    def region_slug(self):
        """ The unique slug identifier for the droplet's region """
        try:
            return self.region.slug
        except (TypeError, AttributeError):
            return None

    @property
    def image_slug(self):
        """
        The unique slug identifier for the droplet's image, or `None` if the
        image doesn't have a slug
        """
        try:
            return self.image.slug
        except (TypeError, AttributeError):
            return None

    @property
    def ip_address(self):
        """
        The IP address of the first interface listed in the droplet's
        ``networks`` field (ordering IPv4 before IPv6), or `None` if there
        are no interfaces
        """
        networks = self.get("networks", {})
        v4nets = networks.get("v4", [])
        v6nets = networks.get("v6", [])
        try:
            return (v4nets + v6nets)[0].ip_address
        except IndexError:
            return None

    @property
    def url(self):
        """ The endpoint for operations on the specific droplet """
        return self._url('/v2/droplets/' + str(self.id))

    def fetch(self):
        """
        Fetch & return a new `Droplet` object representing the droplet's
        current state

        :rtype: Droplet
        :raises DOAPIError: if the API endpoint replies with an error (e.g., if
            the droplet no longer exists)
        """
        api = self.doapi_manager
        return api._droplet(api.request(self.url)["droplet"])

    def fetch_all_neighbors(self):
        r"""
        Returns a generator that yields all of the droplets running on the same
        physical server as the droplet

        :rtype: generator of `Droplet`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        return map(api._droplet, api.paginate(self.url + '/neighbors',
                                             'droplets'))

    def fetch_all_snapshots(self):
        r"""
        Returns a generator that yields all of the snapshot images created from
        the droplet

        :rtype: generator of `Image`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        for obj in api.paginate(self.url + '/snapshots', 'snapshots'):
            yield Image(obj, doapi_manager=api, droplet=self)

    def fetch_all_backups(self):
        r"""
        Returns a generator that yields all of the backup images created from
        the droplet

        :rtype: generator of `Image`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        for obj in api.paginate(self.url + '/backups', 'backups'):
            yield Image(obj, doapi_manager=api, droplet=self)

    def fetch_all_kernels(self):
        r"""
        Returns a generator that yields all of the kernels available to the
        droplet

        :rtype: generator of `Kernel`\ s
        :raises DOAPIError: if the API endpoint replies with an error
        """
        api = self.doapi_manager
        for kern in api.paginate(self.url + '/kernels', 'kernels'):
            yield Kernel(kern, doapi_manager=api, droplet=self)

    def enable_backups(self):
        """
        Enable backups on the droplet

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='enable_backups')

    def disable_backups(self):
        """
        Disable backups on the droplet

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='disable_backups')

    def reboot(self):
        """
        Reboot the droplet

            A reboot action is an attempt to reboot the Droplet in a graceful
            way, similar to using the :command:`reboot` command from the
            console. [APIDocs]_

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='reboot')

    def power_cycle(self):
        """
        Power cycle the droplet

            A powercycle action is similar to pushing the reset button on a
            physical machine, it's similar to booting from scratch. [APIDocs]_

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='power_cycle')

    def shutdown(self):
        """
        Shut down the droplet

            A shutdown action is an attempt to shutdown the Droplet in a
            graceful way, similar to using the :command:`shutdown` command from
            the console.  Since a ``shutdown`` command can fail, this action
            guarantees that the command is issued, not that it succeeds.  The
            preferred way to turn off a Droplet is to attempt a shutdown, with
            a reasonable timeout, followed by a power off action to ensure the
            Droplet is off. [APIDocs]_

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='shutdown')

    def power_off(self):
        """
        Power off the droplet

            A ``power_off`` event is a hard shutdown and should only be used if
            the :meth:`shutdown` action is not successful.  It is similar to
            cutting the power on a server and could lead to complications.
            [APIDocs]_

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='power_off')

    def power_on(self):
        """
        Power on the droplet

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='power_on')

    def restore(self, image):
        """
        Restore the droplet to the specified backup image

            A Droplet restoration will rebuild an image using a backup image.
            The image ID that is passed in must be a backup of the current
            Droplet instance.  The operation will leave any embedded SSH keys
            intact. [APIDocs]_

        :param image: an image ID, an image slug, or an `Image` object
            representing a backup image of the droplet
        :type image: integer, string, or `Image`
        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if isinstance(image, Image):
            image = image.id
        return self.act(type='restore', image=image)

    def password_reset(self):
        """
        Reset the password for the droplet

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='password_reset')

    def resize(self, size, disk=None):
        """
        Resize the droplet

        :param size: a size slug or a `Size` object representing the size to
            resize to
        :type size: string or `Size`
        :param bool disk: Set to `True` for a permanent resize, including
            disk changes
        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if isinstance(size, Size):
            size = size.slug
        opts = {"disk": disk} if disk is not None else {}
        return self.act(type='resize', size=size, **opts)

    def rebuild(self, image):
        """
        Rebuild the droplet with the specified image

            A rebuild action functions just like a new create. [APIDocs]_

        :param image: an image ID, an image slug, or an `Image` object
            representing the image the droplet should use as a base
        :type image: integer, string, or `Image`
        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if isinstance(image, Image):
            image = image.id
        return self.act(type='rebuild', image=image)

    def rename(self, name):
        """
        Rename the droplet

        :param str name: the new name for the droplet
        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='rename', name=name)

    def change_kernel(self, kernel):
        """
        Change the droplet's kernel

        :param kernel: a kernel ID or `Kernel` object representing the new
            kernel
        :type kernel: integer or `Kernel`
        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        if isinstance(kernel, Kernel):
            kernel = kernel.id
        return self.act(type='change_kernel', kernel=kernel)

    def enable_ipv6(self):
        """
        Enable IPv6 networking on the droplet

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='enable_ipv6')

    def enable_private_networking(self):
        """
        Enable private networking on the droplet

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='enable_private_networking')

    def snapshot(self, name):
        """
        Create a snapshot image of the droplet

        :param str name: the name for the new snapshot
        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='snapshot', name=name)

    def upgrade(self):
        """
        Upgrade the droplet

        :return: an `Action` representing the in-progress operation on the
            droplet
        :rtype: Action
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return self.act(type='upgrade')

    def delete(self):
        """
        Delete the droplet

        :return: `None`
        :raises DOAPIError: if the API endpoint replies with an error
        """
        self.doapi_manager.request(self.url, method='DELETE')

    def wait(self, status=None, wait_interval=None, wait_time=None):
        """
        Poll the server periodically until the droplet has reached some final
        state.  If ``status`` is non-`None`, ``wait`` will wait for the
        droplet's ``status`` field to equal the given value; otherwise, it will
        wait for the most recent action on the droplet to finish.

        If ``wait_time`` is exceeded or a `KeyboardInterrupt` is caught, the
        droplet's most recently fetched state is returned immediately without
        waiting for completion.

        :param status: When non-`None`, the desired value for the ``status``
            field of the droplet, which should be one of
            `Droplet.STATUS_ACTIVE`, `Droplet.STATUS_ARCHIVE`,
            `Droplet.STATUS_NEW`, and `Droplet.STATUS_OFF`.  (For the sake of
            forwards-compatibility, any other value is accepted as well.)
        :type status: string or `None`
        :param number wait_interval: how many seconds to sleep between
            requests; defaults to the `doapi` object's
            :attr:`~doapi.wait_interval` if not specified or `None`
        :param number wait_time: the total number of seconds after which the
            method will return, or a negative number to wait indefinitely;
            defaults to the `doapi` object's :attr:`~doapi.wait_time` if not
            specified or `None`
        :return: the droplet's final state
        :rtype: Droplet
        :raises DOAPIError: if the API endpoint replies with an error
        """
        return next(self.doapi_manager.wait_droplets([self], status,
                                                     wait_interval, wait_time))
