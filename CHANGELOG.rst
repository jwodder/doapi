v0.3.0 (in development)
-----------------------
- Support for block storage volumes:

  - new ``Volume`` class
  - new ``doapi`` methods:

    - ``doapi.act_on_volume_by_name()``
    - ``doapi.attach_volume_by_name()``
    - ``doapi.create_volume()``
    - ``doapi.delete_volume_by_name()``
    - ``doapi.detach_volume_by_name()``
    - ``doapi.fetch_all_volumes()``
    - ``doapi.fetch_volume()``

  - ``doapi.create_droplet`` now takes an optional ``volumes`` argument


v0.2.0 (2016-08-30)
-------------------
- Support for tags:

  - new ``Tag`` class with methods for acting on all droplets with a given tag
    at once
  - new ``doapi.fetch_tag()``, ``doapi.fetch_all_tags()``, and
    ``doapi.create_tag()`` methods
  - new ``Droplet.tag()`` and ``Droplet.untag()`` methods
  - The ``doapi.fetch_all_droplets()`` method can now optionally take a
    ``tag_name`` argument
  - new ``doapi-tag`` command
  - Applicable subcommands of ``doapi-droplet`` now accept a ``--tag <TAG>``
    option in order to specify what droplets to operate on

- **Breaking**: "Wait" methods now raise a ``WaitTimeoutError`` if
  ``wait_time`` is exceeded
- **Breaking**: ``doapi.wait_droplets()`` and ``Droplet.wait()`` no longer have
  the option to wait for droplets' most recent actions to complete; that
  functionality has been split into ``doapi.wait_actions_on_objects()`` and
  ``Droplet.wait_for_action()``, respectively
- **Breaking**: Renamed the ``wait`` methods of ``Image`` and ``FloatingIP`` to
  ``wait_for_action``
- **Breaking**: ``--multiple`` now also matches by ID, slug, & fingerprint
- **Breaking**: Removed the ``droplet`` attribute and ``fetch_droplet`` method
  from ``BackupWindow``, ``Image``, ``Kernel``, ``Networks``, and
  ``NetworkInterface``
- **Breaking**: ``doapi-droplet snapshot`` can now operate on multiple droplets
  at once, and its syntax has changed to require the snapshot name before the
  droplet names.

- New methods:

  - ``doapi.wait_actions_on_objects()``
  - ``Action.raise_for_error()`` (raises a new ``ActionError`` exception)
  - ``FloatingIP.__int__()``
  - ``Resource.for_json()``

- Gave ``doapi.wait_droplets()`` and ``Droplet.wait()`` a ``locked`` parameter
  for waiting for droplets to become locked/unlocked
- Gave ``doapi-droplet wait`` ``--locked`` and ``--unlocked`` options
- Removed droplet upgrade code, as the API no longer supports it
- Gave ``Droplet`` ``ipv4_address`` and ``ipv6_address`` attributes
- Decreased the default wait interval to 2 seconds
- Handle fetching the last action on a resource that has never been acted on
- The ``wait_for_action`` methods now return ``None`` if the resource no longer
  exists by the time the action completes
- Gave the ``--wait`` option a ``-w`` short form
- The ``private`` argument to ``doapi.fetch_all_images()`` now defaults to
  ``None``; if set to ``False``, the value will be passed through to the API
  (not that this currently has any effect).


v0.1.1 (2016-04-29)
-------------------
- **Bugfix**: Fixed a bug with creating droplets with SSH keys from the command
  line


v0.1.0 (2016-04-07)
-------------------
Initial release
