v0.2.0 (in development)
-----------------------
- **Breaking**: "Wait" methods now raise a ``WaitTimeoutError`` if
  ``wait_time`` is exceeded
- **Breaking**: Renamed the ``wait`` method of ``Droplet``, ``Image``, and
  ``FloatingIP`` to ``wait_for_action``
- **Breaking**: ``doapi.wait_droplets`` and ``Droplet.wait`` no longer have the
  option to wait for droplets' most recent actions to complete
- **Breaking**: ``--multiple`` now also matches by ID, slug, & fingerprint
- New methods:

    - ``doapi.wait_actions_on_objects``
    - ``Action.raise_for_error`` (raises a new ``ActionError`` exception)
    - ``Resource.for_json``

- Added a ``for_json`` function
- Gave ``doapi.wait_droplets`` and ``Droplet.wait`` a ``locked`` parameter for
  waiting for droplets to become locked/unlocked
- Removed droplet upgrade code, as the API no longer supports it

v0.1.1 (2016-04-29)
-------------------
- Fixed a bug with creating droplets with SSH keys from the command line

v0.1.0 (2016-04-07)
-------------------
Initial release
