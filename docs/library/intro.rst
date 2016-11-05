.. currentmodule:: doapi

Introduction
------------

.. todo::

    Organize this better

.. todo::

    Document potential weirdness when accessing ``doapi.last_*`` while a
    generator is being evaluated

..
    doapi doesn't do any caching; you have to do it yourself.

Under normal circumstances, the ``fetch`` and ``fetch_all_*`` methods of a
resource will only raise a `DOAPIError` if the resource no longer exists.

Generators producing objects always yield them in whatever order the API
endpoint returns them in.

If you want all paginated results to be fetched at once, wrap the generator in
`list()`.

Passing objects produced by one `doapi` object to methods of another results in
undefined behavior.


.. _resources:

Resource Objects
^^^^^^^^^^^^^^^^

.. todo::

    Document `.doapi_manager`, dict/mapping methods, and conversion to a dict

    Document that you can copy a Resource object by passing it to the
    constructor for its class?

Instances of classes representing DigitalOcean API resources — i.e., `Account`,
`Action`, `BackupWindow`, `Domain`, `DomainRecord`, `Droplet`, `FloatingIP`,
`Image`, `Kernel`, `NetworkInterface`, `Networks`, `Region`, `SSHKey`, `Size`,
and `Tag` — make their API fields available in three different ways:

- as regular object attributes: ``droplet.id``
- via indexing: ``droplet["id"]``
- via indexing the ``fields`` dictionary attribute: ``droplet.fields["id"]``

Modifying a resource object's fields only affects your local copy of the
resource's data; to actually modify the resource on DigitalOcean's servers,
call one of the object's methods.

Note that calling a mutating method on a resource object simply sends a request
to the API endpoint and does not modify the local Python object.  To get the
most up-to-date information on a resource, you must call the resource object's
``fetch`` method to acquire a new object.

Note that resource objects have whatever attributes the API returns them with,
which may or may not be the same set of attributes as the documentation says
they should have.  Also note that only documented attributes are ever converted
to custom classes; e.g., if the API suddenly returns an SSH key with a
``"region"`` field, the region data will be left as a `dict` rather than
converted to a `Region`.

All resource objects have the following method:

.. automethod:: Resource.for_json
