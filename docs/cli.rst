.. module:: doapi

Command-Line Programs
=====================

.. toctree::
   :maxdepth: 1

   cli/account
   cli/action
   cli/domain
   cli/droplet
   cli/floating_ip
   cli/image
   cli/region
   cli/request
   cli/size
   cli/sshkey

TODO

[Document the plain :program:`doapi` command]

----

.. _universal:

Universal Options
-----------------

All commands take the following options in addition to those listed in their
individual documentation:

.. option:: --api-token <token>

    Use ``<token>`` as an OAuth token for authentication with the API; mutually
    exclusive with ``--api-token-file``

.. option:: --api-token-file <file>

    Use the contents of ``<file>`` as an OAuth token for authentication with
    the API; mutually exclusive with ``--api-token``

.. option:: --endpoint <URL>

    Use ``<URL>`` as the base URL for all API requests; default value:
    ``https://api.digitalocean.com`` (the official DigitalOcean API endpoint)

.. option:: --timeout <seconds>

    The maximum number of seconds to wait when attempting to connect to or read
    from the remote endpoint; default value: no timeout

Note that these options cannot be attached to subcommands::

    doapi-droplet --timeout 1000 show  # Good
    doapi --timeout 1000 droplet show  # Good
    doapi-droplet show --timeout 1000  # Bad!

----

In order to perform API requests, an OAuth token must be supplied to
:program:`doapi` so that it can authenticate with the DigitalOcean server.  You
can generate an OAuth token for your account via the `"Apps & API" section
<https://cloud.digitalocean.com/settings/applications>`_ of your DigitalOcean
account's control panel.

The :program:`doapi` commands will look for an OAuth token in the following
locations, in order:

1. Specified on the command line with ``--api-token <token>`` or
   ``--api-token-file <file>``
2. The value of the :envvar:`DO_API_TOKEN` environment variable
3. The contents of a ``.doapi`` file in your home directory

----

.. _waitopts:

Options common to all subcommands that produce `Action` objects::

    --wait
    --wait-time seconds
    --wait-interval seconds

----

::

    <droplet> := ID or name
    <sshkey>  := ID, fingerprint, or name
    <image>   := ID, slug, or name (slugs take precedence)
    <action>  := ID
    <ip>      := IP address in x.x.x.x form or as an integer
