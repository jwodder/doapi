.. module:: doapi

Library
=======

.. toctree::
   library/doapi
   library/droplets
   library/domain
   library/misc
   library/extra
   library/examples

Generators producing objects always yield them in whatever order the API
endpoint returns them in.

All public non-magic methods perform API requests and may raise a `DOAPIError`.

Note that calling a mutating method on a resource object simply sends a request
to the API endpoint and does not modify the local Python object.  To get the
most up-to-date information on a resource, you must call the resource object's
``fetch`` method to acquire a new object.

Under normal circumstances, the ``fetch`` and ``fetch_all_*`` methods of a
resource will only raise a `DOAPIError` if the resource no longer exists.
