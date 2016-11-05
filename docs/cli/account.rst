.. currentmodule:: doapi

:program:`doapi-account`
------------------------

NAME
^^^^

:program:`doapi-account` — fetch DigitalOcean account data

SYNOPSIS
^^^^^^^^

::

    doapi-account [<universal options>] [--rate-limit]

DESCRIPTION
^^^^^^^^^^^

:program:`doapi-account` displays the current information about your
DigitalOcean account as available via the API.  The account information is
output as an `Account` object converted to JSON.

OPTIONS
^^^^^^^

In addition to the :ref:`universal options <universal>` common to all
:program:`doapi` commands, :program:`doapi-account` takes the following:

.. program:: doapi-account

.. option:: --rate-limit

    Fetch the account data, but instead of displaying it, output the rate limit
    headers from the response.  (The account data is only requested so that
    there's a response to get the headers from.)
