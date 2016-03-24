.. module:: doapi

:program:`doapi-request`
------------------------

NAME
^^^^

:program:`doapi-request` — perform a raw DigitalOcean API request

SYNOPSIS
^^^^^^^^

::

    doapi-request [<universal options>]
                  [-d|--data <string|@file>]
                  [-D|--dump-header <file>]
                  [--paginate <key>]
                  [-X|--request <method>]
                  <URL>|<path>

DESCRIPTION
^^^^^^^^^^^

:program:`doapi-request` makes a request to a DigitalOcean API endpoint and
outputs the response as readably-formatted JSON.  It's like a
DigitalOcean-centric :manpage:`curl(1)` that doesn't make you type out your API
token every time, with an option for handling pagination.

A request can be made either to an absolute URL or to a path like
``/v2/account`` that will be appended to the API endpoint in use.

OPTIONS
^^^^^^^

In addition to the :ref:`universal options <universal>` common to all
:program:`doapi` commands, :program:`doapi-request` takes the following:

.. program:: doapi-request

.. option:: -d <data>, --data <data>

    Send the given data (which must be valid JSON) in the body of the request.
    If ``<data>`` begins with "``@``", the rest of the argument (if there is
    any) is treated as a file from which to read the data; a filename of ``-``
    causes data to be read from standard input.

    :option:`--data` and :option:`--paginate` are mutually exclusive.

.. option:: -D <file>, --dump-header <file>

    Dump the headers of the HTTP response as a JSON object to the given file.
    If :option:`--paginate` is also used, only the headers for the last
    response will be dumped.  ``<file>`` may be ``-`` to write the headers to
    standard output.

.. option:: --paginate <key>

    (``GET`` method only) Assume that the API will respond with a `paginated
    <https://developers.digitalocean.com/documentation/v2/#links>`_ list of one
    or more values, i.e., an object containing a field ``<key>`` mapped to a
    list of values and a field ``"links"`` containing a URL for retrieving the
    next set of values in the result list, if any.  Instead of performing a
    single request and outputting the response body, :program:`doapi-requests`
    will perform multiple requests to retrieve all of the pages and will output
    a concatenated list of all of the values in the ``<key>`` field of each
    page.

    :option:`--data` and :option:`--paginate` are mutually exclusive.

.. option:: -X <method>, --request <method>

    Specifies the HTTP method to use for the request.  Valid options are
    ``GET`` (the default), ``POST``, ``PUT``, and ``DELETE`` (case
    insensitive).

    When the ``DELETE`` method is used, no output (other than that for
    :option:`--dump-header`, if specified) will be produced.
