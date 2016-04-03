.. module:: doapi

Library
=======

.. toctree::
   doapi
   droplets
   domain
   floating_ip
   image
   ssh_key
   immutable
   utils
   examples

Generators producing objects always yield them in whatever order the API
endpoint returns them in.

All public non-magic methods perform API requests and may raise a `DOAPIError`.

Note that calling a mutating method on a resource object simply sends a request
to the API endpoint and does not modify the local Python object.  To get the
most up-to-date information on a resource, you must call the resource object's
``fetch`` method to acquire a new object.

Under normal circumstances, the ``fetch`` and ``fetch_all_*`` methods of a
resource will only raise a `DOAPIError` if the resource no longer exists.


[Note that resource objects have whatever attributes the API returns them with,
which may or may not be the same set of attributes as the documentation says
they should have.  Also note that any extra attributes that a resource may have
that are not specified in the API docs will not be processed into non-JSON
types.]

Passing objects produced by one `doapi` object to methods of another results in
undefined behavior.

[Document potential weirdness when accessing ``doapi.last_*`` while a generator
is being evaluated]
