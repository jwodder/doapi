doapi — DigitalOcean API Python library & CLI
=============================================

.. |repostatus| image:: http://www.repostatus.org/badges/latest/wip.svg
    :alt: Project Status: WIP - Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.
    :target: http://www.repostatus.org/#wip

|repostatus| *(Until v1.0 is released, backwards compatibility will be broken at will.)*

..
    `GitHub <https://github.com/jwodder/doapi>`_
    PyPI
    Readthedocs

As yet another Python wrapper library for version 2 of the `DigitalOcean
<https://www.digitalocean.com>`_ `API
<https://developers.digitalocean.com/documentation/v2/>`_, ``doapi`` offers:

- Individual methods for every operation listed in the API docs plus methods
  for making arbitrary "freeform" requests
- Connection pooling via `requests' <http://www.python-requests.org>`_ `Session
  objects
  <http://www.python-requests.org/en/master/user/advanced/#session-objects>`_
- Paginated results are returned as generators that make requests when
  necessary, so your account's entire action history isn't fetched all at once
- Methods for waiting for multiple droplets to come up or multiple actions to
  complete in parallel
- A command-line interface to all of the above

..
    - The CLI outputs the same JSON values as returned by the API, but made
      readable; perfect for ``jq``