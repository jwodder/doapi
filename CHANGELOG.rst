v0.2.0 (in development)
-----------------------
- **Breaking**: "Wait" methods now raise a ``WaitTimeoutError`` if
  ``wait_time`` is exceeded
- **Breaking**: Renamed the ``wait`` method of ``Droplet``, ``Image``, and
  ``FloatingIP`` to ``wait_for_action``
- **Breaking**: ``doapi.wait_droplets`` and ``Droplet.wait`` no longer have the
  option to wait for droplets' most recent actions to complete
- **Breaking**: ``--multiple`` now also matches by ID, slug, & fingerprint
- **Breaking**: Removed the ``droplet`` attribute and ``fetch_droplet`` method
  from ``BackupWindow``, ``Image``, ``Kernel``, ``Networks``, and
  ``NetworkInterface``
- New methods:

    - ``doapi.wait_actions_on_objects``
    - ``Action.raise_for_error`` (raises a new ``ActionError`` exception)
    - ``FloatingIP.__int__``
    - ``Resource.for_json``

- Gave ``doapi.wait_droplets`` and ``Droplet.wait`` a ``locked`` parameter for
  waiting for droplets to become locked/unlocked
- Gave ``doapi-droplet wait`` ``--locked`` and ``--unlocked`` options
- Removed droplet upgrade code, as the API no longer supports it
- Gave ``Droplet`` ``ipv4_address`` and ``ipv6_address`` attributes
- Decreased the default wait interval to 2 seconds
- Handle fetching the last action on a resource that has never been acted on
- The ``wait_for_action`` methods now return ``None`` if the resource no longer
  exists by the time the action completes
- Gave the ``--wait`` option a ``-w`` short form
- The ``private`` argument to ``doapi.fetch_all_images`` now defaults to
  ``None``; if set to ``False``, the value will be passed through to the API
  (not that this currently has any effect).

v0.1.1 (2016-04-29)
-------------------
- **Bugfix**: Fixed a bug with creating droplets with SSH keys from the command
  line

v0.1.0 (2016-04-07)
-------------------
Initial release
