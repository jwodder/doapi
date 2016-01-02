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

[Document the plain ``doapi`` command]

----

All commands take the following options:

``--api-token <token>``
    Use ``<token>`` as an OAuth token for authentication with the API; mutually
    exclusive with ``--api-token-file``

``--api-token-file <file>``
    Use the contents of ``<file>`` as an OAuth token for authentication with
    the API; mutually exclusive with ``--api-token``

``--timeout <seconds>``
    The ``timeout`` value to use when making API requests; default value: 61.
    See http://www.python-requests.org/en/latest/user/advanced/#timeouts for
    more information.

``--endpoint <URL>``
    Use ``<URL>`` as the base URL for all API requests; default value:
    ``https://api.digitalocean.com`` (the official DigitalOcean API endpoint)

Note that these options cannot be attached to subcommands::

    doapi-droplet --timeout 1000 show  # Good
    doapi --timeout 1000 droplet show  # Good
    doapi-droplet show --timeout 1000  # Bad!

----

In order to perform API requests, an OAuth token must be supplied to ``doapi``
so that it can authenticate with the DigitalOcean server.  You can generate an
OAuth token for your account via the `"Apps & API" section
<https://cloud.digitalocean.com/settings/applications>`_ of your DigitalOcean
account's control panel.

The ``doapi`` commands will look for an OAuth token in the following locations,
in order:

1. Specified on the command line with ``--api-token <token>`` or
   ``--api-token-file <file>``
2. The value of the ``DO_API_TOKEN`` environment variable
3. The contents of a ``.doapi`` file in your home directory

----

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
