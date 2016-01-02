.. module:: doapi

``doapi-request``
-----------------

NAME
^^^^

``doapi-request`` — perform a raw DigitalOcean API request

SYNOPSIS
^^^^^^^^

::

    doapi-request [<universal options>]
        [-X|--request <method>]
        [-d|--data <string|@file>]
        [-D|--dump-header <file>]
        [--paginate <key>]
        <URL>|<path>

``-d`` and ``-D`` are interpreted as for ``curl(1)``.

``--dump-header`` dumps as JSON, because it's much easier that way.
