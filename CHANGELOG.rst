v0.2.0 (in development)
-----------------------
- Added ``Action.raise_for_error`` method and an ``ActionError`` exception
- Gave Resource objects a ``for_json`` method and added a ``for_json`` function
- **Breaking**: "Wait" methods now raise a ``WaitTimeoutError`` if
  ``wait_time`` is exceeded
- Gave ``doapi.wait_droplets`` and ``Droplet.wait`` a ``locked`` parameter for
  waiting for droplets to become locked/unlocked
- **Breaking**: ``--multiple`` now also matches by ID, slug, & fingerprint
- **Breaking**: Renamed the ``wait`` method of ``Droplet``, ``Image``, and
  ``FloatingIP`` to ``wait_for_action``
- Removed droplet upgrade code, as the API no longer supports it

v0.1.1 (2016-04-29)
-------------------
- Fixed a bug with creating droplets with SSH keys from the command line

v0.1.0 (2016-04-07)
-------------------
Initial release
