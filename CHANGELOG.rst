v0.2.0 (in development)
-----------------------
- Added ``Action.raise_for_error`` method and an ``ActionError`` exception
- Gave Resource objects a ``for_json`` method and added a ``for_json`` function
- **Breaking**: "Wait" methods now raise a ``WaitTimeoutError`` if
  ``wait_time`` is exceeded

v0.1.0 (2016-04-07)
-------------------
Initial release
