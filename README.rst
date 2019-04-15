doapi — DigitalOcean API Python library & CLI
=============================================

.. |pypi| image:: https://img.shields.io/pypi/v/doapi.svg
    :target: https://pypi.python.org/pypi/doapi

.. |repostatus| image:: https://www.repostatus.org/badges/latest/abandoned.svg
    :target: https://www.repostatus.org/#abandoned
    :alt: Project Status: Abandoned – Initial development has started, but there
          has not yet been a stable, usable release; the project has been
          abandoned and the author(s) do not intend on continuing development.

.. |RTD| image:: https://readthedocs.org/projects/doapi/badge/?version=stable
    :target: http://doapi.readthedocs.io/en/latest/?badge=stable
    :alt: Read the Docs

.. |license| image:: https://img.shields.io/github/license/jwodder/doapi.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

|pypi| |repostatus| |RTD| |license|

*(Until v1.0 is released, backwards compatibility will be broken at will.)*

As yet another Python wrapper library for version 2 of the `DigitalOcean
<https://www.digitalocean.com>`_ `API
<https://developers.digitalocean.com/documentation/v2/>`_, ``doapi`` offers:

- Individual methods for every operation listed in the API docs plus methods
  for making arbitrary "freeform" requests or actions
- Methods for waiting for multiple droplets to come up or multiple actions to
  complete in parallel (and if you get tired of waiting, you can hit Cntrl-C to
  make the methods return immediately)
- Connection pooling via `requests' <http://www.python-requests.org>`_ `Session
  objects
  <http://www.python-requests.org/en/master/user/advanced/#session-objects>`_
- Paginated results are returned as generators that make requests when
  necessary, so your account's entire action history isn't fetched all at once
- A command-line interface to all of the above that outputs JSON objects in the
  same format as used by the API (perfect for massaging with `jq
  <https://stedolan.github.io/jq/>`_!)
- When creating droplets from the command line, new SSH public keys can be
  specified without having to register them explicitly beforehand.
